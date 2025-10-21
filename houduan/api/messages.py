from __future__ import annotations

from flask import jsonify, request
from flask_login import login_required

from . import api_bp
from ..app import db
from ..models import Message
from ..services.message_handler import process_message


@api_bp.get("/messages")
@login_required
def list_messages():
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
            items = session.query(Message).order_by(Message.id.desc()).limit(50).all()
            return jsonify([
                {
                    "id": m.id,
                    "shop_id": m.shop_id,
                    "customer_id": m.customer_id,
                    "content": m.content,
                    "content_preview": (m.content or "")[:80],
                    "source": m.source,
                    "status": m.status,
                    "handled_by": m.handled_by,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in items
            ])
        finally:
            session.close()
    except Exception as e:
        print(f"Error in list_messages: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/messages/process")
@login_required
def process_message_api():
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        msg_id = data.get("message_id")
        if not msg_id:
            return jsonify({"error": "message_id_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            m = session.get(Message, int(msg_id))
            if not m:
                return jsonify({"error": "message_not_found"}), 404
            result = process_message(m)
            return jsonify({
                "reply": result.reply,
                "source": result.source,
                "auto_send": result.auto_send,
                "confidence": result.confidence,
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in process_message_api: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500