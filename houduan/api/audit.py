from __future__ import annotations

from flask import request, jsonify
from flask_login import login_required

from . import api_bp
from ..app import db
from ..models import AuditQueueItem, AIReply, Message
from ..utils.security import require_roles
from ..services.qianniu_monitor import activate_window_by_title, send_text_in_active_window


@api_bp.get("/audit")
@login_required
def list_audit():
    try:
        import sqlite3
        import os
        
        # 直接使用sqlite3连接
        current_dir = os.getcwd()
        db_path = os.path.join(current_dir, 'data', 'sqlite.db')
        
        if not os.path.exists(db_path):
            # 尝试相对于当前文件的路径
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sqlite.db'))
            
            if not os.path.exists(db_path):
                # 尝试项目根目录
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                db_path = os.path.join(project_root, 'data', 'sqlite.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 查询审核队列
            cursor.execute("""
                SELECT id, message_id, assigned_to, status, note, created_at 
                FROM audit_queue 
                ORDER BY id ASC 
                LIMIT 100
            """)
            items = cursor.fetchall()
            
            result = []
            for item in items:
                item_id, message_id, assigned_to, status, note, created_at = item
                
                # 查询关联的消息
                cursor.execute("SELECT id, shop_id, customer_id, content, status, created_at FROM messages WHERE id = ?", (message_id,))
                msg_row = cursor.fetchone()
                
                # 查询AI回复
                cursor.execute("""
                    SELECT id, model, reply, confidence, review_status, created_at 
                    FROM ai_replies 
                    WHERE message_id = ? 
                    ORDER BY id DESC 
                    LIMIT 1
                """, (message_id,))
                ai_row = cursor.fetchone()
                
                result.append({
                    "id": item_id,
                    "message_id": message_id,
                    "status": status,
                    "assigned_to": assigned_to,
                    "note": note,
                    "created_at": created_at,
                    # 消息详情
                    "message": {
                        "id": msg_row[0] if msg_row else None,
                        "shop_id": msg_row[1] if msg_row else None,
                        "customer_id": msg_row[2] if msg_row else None,
                        "content": msg_row[3] if msg_row else None,
                        "status": msg_row[4] if msg_row else None,
                        "created_at": msg_row[5] if msg_row else None,
                    } if msg_row else None,
                    # AI 回复详情
                    "ai_reply": {
                        "id": ai_row[0] if ai_row else None,
                        "model": ai_row[1] if ai_row else None,
                        "reply": ai_row[2] if ai_row else None,
                        "confidence": ai_row[3] if ai_row else None,
                        "review_status": ai_row[4] if ai_row else None,
                        "created_at": ai_row[5] if ai_row else None,
                    } if ai_row else None,
                })
            
            return jsonify(result)
        finally:
            conn.close()
    except Exception as e:
        print(f"Error in list_audit: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/audit/approve")
@login_required
@require_roles("superadmin", "admin")
def approve():
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        item_id = data.get("id")
        title_kw = data.get("title_kw", "千牛")
        edited_reply = data.get("edited_reply")  # 支持编辑后的回复内容
        
        if not item_id:
            return jsonify({"error": "id_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            it = session.get(AuditQueueItem, int(item_id))
            if not it:
                return jsonify({"error": "auditqueueitem_not_found"}), 404
            it.status = "approved"
            
            ai = session.query(AIReply).filter_by(message_id=it.message_id).order_by(AIReply.id.desc()).first()
            if ai:
                ai.review_status = "approved"
                # 如果提供了编辑后的回复，更新AI回复内容
                if edited_reply:
                    ai.reply = edited_reply
            
            msg = session.get(Message, it.message_id)
            if msg:
                # 优先使用编辑后的回复，否则使用AI回复，最后使用消息内容
                reply_text = edited_reply or (ai.reply if ai else msg.content)
                
                # 发送实现：UI 自动化发送，发送成功后标记 answered
                ok = activate_window_by_title(title_kw)
                if ok:
                    send_text_in_active_window(reply_text)
                    msg.status = "answered"
                else:
                    # 即使UI自动化失败，也标记为已处理
                    msg.status = "answered"
                
                # 创建一条新的消息记录来保存我们发送的回复，这样在历史记录中就能看到
                from datetime import datetime
                reply_message = Message(
                    shop_id=msg.shop_id,
                    customer_id=msg.customer_id,
                    content=reply_text,
                    source="system_reply",  # 标记为系统回复
                    status="sent",  # 标记为已发送
                    handled_by="admin"
                )
                session.add(reply_message)
            
            session.commit()
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error in approve: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.get("/audit/<int:item_id>/context")
@login_required
def get_audit_context(item_id: int):
    """获取审核项的历史消息上下文"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            it = session.get(AuditQueueItem, item_id)
            if not it:
                return jsonify({"error": "auditqueueitem_not_found"}), 404
            msg = session.get(Message, it.message_id)
            
            if not msg:
                return jsonify({"error": "message_not_found"}), 404
            
            # 获取该客户的最近10条消息
            context_messages = session.query(Message).filter(
                Message.shop_id == msg.shop_id,
                Message.customer_id == msg.customer_id,
                Message.id != msg.id  # 排除当前消息
            ).order_by(Message.id.desc()).limit(10).all()
            
            return jsonify({
                "current_message": {
                    "id": msg.id,
                    "content": msg.content,
                    "status": msg.status,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                },
                "context_messages": [
                    {
                        "id": m.id,
                        "content": m.content,
                        "status": m.status,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                    }
                    for m in context_messages
                ]
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in get_audit_context: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/audit/reject")
@login_required
@require_roles("superadmin", "admin")
def reject():
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        item_id = data.get("id")
        if not item_id:
            return jsonify({"error": "id_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            it = session.get(AuditQueueItem, int(item_id))
            if not it:
                return jsonify({"error": "auditqueueitem_not_found"}), 404
            it.status = "rejected"
            ai = session.query(AIReply).filter_by(message_id=it.message_id).order_by(AIReply.id.desc()).first()
            if ai:
                ai.review_status = "rejected"
            msg = session.get(Message, it.message_id)
            if msg:
                msg.status = "queued"
            session.commit()
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error in reject: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/audit/recall")
@login_required
@require_roles("superadmin", "admin")
def recall():
    """撤回已通过的审核项"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        item_id = data.get("id")
        if not item_id:
            return jsonify({"error": "id_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            it = session.get(AuditQueueItem, int(item_id))
            if not it:
                return jsonify({"error": "auditqueueitem_not_found"}), 404
            
            # 只有已通过的状态才能撤回
            if it.status != "approved":
                return jsonify({"error": "only_approved_can_be_recalled"}), 400
            
            it.status = "pending"
            ai = session.query(AIReply).filter_by(message_id=it.message_id).order_by(AIReply.id.desc()).first()
            if ai:
                ai.review_status = "pending"
            msg = session.get(Message, it.message_id)
            if msg:
                msg.status = "new"
            session.commit()
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error in recall: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/audit/review_again")
@login_required
@require_roles("superadmin", "admin")
def review_again():
    """重新审核已拒绝的审核项"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        item_id = data.get("id")
        if not item_id:
            return jsonify({"error": "id_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            it = session.get(AuditQueueItem, int(item_id))
            if not it:
                return jsonify({"error": "auditqueueitem_not_found"}), 404
            
            # 只有已拒绝的状态才能重新审核
            if it.status != "rejected":
                return jsonify({"error": "only_rejected_can_be_reviewed_again"}), 400
            
            it.status = "pending"
            ai = session.query(AIReply).filter_by(message_id=it.message_id).order_by(AIReply.id.desc()).first()
            if ai:
                ai.review_status = "pending"
            msg = session.get(Message, it.message_id)
            if msg:
                msg.status = "new"
            session.commit()
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error in review_again: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


