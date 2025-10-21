from __future__ import annotations

from flask import request, jsonify
from flask_login import login_required

from ..app import db
from ..models import Shop
from ..utils.security import require_roles
from . import api_bp


@api_bp.get("/shops")
@login_required
def list_shops():
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
            items = session.query(Shop).order_by(Shop.id.desc()).all()
            result = []
            for s in items:
                # 解析配置JSON
                config = {}
                if s.config_json:
                    try:
                        import json as _json
                        config = _json.loads(s.config_json)
                    except Exception:
                        config = {}
                
                result.append({
                    "id": s.id, 
                    "name": s.name, 
                    "qianniu_title": s.qianniu_title,
                    "ocr_region": config.get("ocr_region", []),
                    "unread_threshold": config.get("unread_threshold", None),
                    "ai_model": config.get("ai_model", "stub"),
                    "auto_mode": config.get("auto_mode", False),
                    "blacklist": config.get("blacklist", []),
                    "whitelist": config.get("whitelist", []),
                    "business_hours": config.get("business_hours", None),
                    "reply_delay": config.get("reply_delay", 2)
                })
            
            return jsonify(result)
        finally:
            session.close()
    except Exception as e:
        print(f"Error in list_shops: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/shops")
@login_required
@require_roles("superadmin", "admin")
def create_shop():
    try:
        import sqlite3
        import os
        from datetime import datetime
        
        data = request.get_json(force=True)
        name = data.get("name", "").strip()
        qianniu_title = data.get("qianniu_title")
        if not name:
            return jsonify({"error": "name_required"}), 400
        
        # 调试：打印接收到的数据
        print(f"Received data: {data}")
        
        # 构建配置JSON
        config_data = {
            "ocr_region": data.get("ocr_region", []),
            "unread_threshold": data.get("unread_threshold", 0.02),
            "ai_model": data.get("ai_model", "stub"),
            "auto_mode": data.get("auto_mode", False),
            "blacklist": data.get("blacklist", []),
            "whitelist": data.get("whitelist", []),
            "business_hours": data.get("business_hours", None),
            "reply_delay": data.get("reply_delay", 2)
        }
        
        import json as _json
        config_json = _json.dumps(config_data, ensure_ascii=False)
        
        # 直接使用sqlite3连接
        # 使用相对路径，避免中文字符问题
        current_dir = os.getcwd()
        db_path = os.path.join(current_dir, 'data', 'sqlite.db')
        print(f"Current directory: {current_dir}")
        print(f"Database path: {db_path}")
        print(f"Database exists: {os.path.exists(db_path)}")
        
        # 如果相对路径不存在，尝试其他路径
        if not os.path.exists(db_path):
            # 尝试相对于当前文件的路径
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sqlite.db'))
            print(f"Trying alternative path: {db_path}")
            print(f"Alternative path exists: {os.path.exists(db_path)}")
            
            if not os.path.exists(db_path):
                # 尝试项目根目录
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                db_path = os.path.join(project_root, 'data', 'sqlite.db')
                print(f"Trying project root: {db_path}")
                print(f"Project root path exists: {os.path.exists(db_path)}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 插入新店铺
            cursor.execute("""
                INSERT INTO shops (name, qianniu_title, config_json, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (name, qianniu_title, config_json, datetime.now().isoformat(), datetime.now().isoformat()))
            
            shop_id = cursor.lastrowid
            conn.commit()
            
            return jsonify({
                "id": shop_id, 
                "name": name, 
                "qianniu_title": qianniu_title
            })
        finally:
            conn.close()
    except Exception as e:
        print(f"Error in create_shop: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.put("/shops/<int:shop_id>")
@login_required
@require_roles("superadmin", "admin")
def update_shop(shop_id: int):
    try:
        import sqlite3
        import os
        from datetime import datetime
        
        data = request.get_json(force=True)
        
        # 构建配置JSON
        config_data = {
            "ocr_region": data.get("ocr_region", []),
            "unread_threshold": data.get("unread_threshold", 0.02),
            "ai_model": data.get("ai_model", "stub"),
            "auto_mode": data.get("auto_mode", False),
            "blacklist": data.get("blacklist", []),
            "whitelist": data.get("whitelist", []),
            "business_hours": data.get("business_hours", None),
            "reply_delay": data.get("reply_delay", 2)
        }
        
        import json as _json
        config_json = _json.dumps(config_data, ensure_ascii=False)
        
        # 直接使用sqlite3连接
        # 使用相对路径，避免中文字符问题
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
            # 检查店铺是否存在
            cursor.execute("SELECT id FROM shops WHERE id = ?", (shop_id,))
            if not cursor.fetchone():
                return jsonify({"error": "shop_not_found"}), 404
            
            # 更新店铺信息
            update_fields = []
            update_values = []
            
            if "name" in data:
                update_fields.append("name = ?")
                update_values.append(data["name"].strip())
            
            if "qianniu_title" in data:
                update_fields.append("qianniu_title = ?")
                update_values.append(data["qianniu_title"])
            
            # 总是更新配置JSON
            update_fields.append("config_json = ?")
            update_values.append(config_json)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(shop_id)
                
                cursor.execute(f"""
                    UPDATE shops 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
                
                conn.commit()
            
            return jsonify({"ok": True})
        finally:
            conn.close()
    except Exception as e:
        print(f"Error in update_shop: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.delete("/shops/<int:shop_id>")
@login_required
@require_roles("superadmin")
def delete_shop(shop_id: int):
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from ..models import Message, KnowledgeBaseItem, ReplyTemplate, User
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            shop = session.get(Shop, shop_id)
            if not shop:
                return jsonify({"error": "shop_not_found"}), 404
            
            # 先删除相关的数据（外键约束）
            # 删除相关消息
            session.query(Message).filter_by(shop_id=shop_id).delete()
            
            # 删除相关知识库条目
            session.query(KnowledgeBaseItem).filter_by(shop_id=shop_id).delete()
            
            # 删除相关回复模板
            session.query(ReplyTemplate).filter_by(shop_id=shop_id).delete()
            
            # 将相关用户设置为无店铺
            session.query(User).filter_by(shop_id=shop_id).update({"shop_id": None})
            
            # 最后删除店铺
            session.delete(shop)
            session.commit()
            
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error in delete_shop: {e}")
        return jsonify({"error": "delete_failed", "detail": str(e)}), 500


@api_bp.get("/shops/<int:shop_id>/config")
@login_required
def get_shop_config(shop_id: int):
    shop = db.session.get(Shop, shop_id)
    if not shop:
        return jsonify({"error": "shop_not_found"}), 404
    import json as _json
    cfg = {}
    if shop.config_json:
        try:
            cfg = _json.loads(shop.config_json)
        except Exception:
            cfg = {}
    return jsonify(cfg)


@api_bp.put("/shops/<int:shop_id>/config")
@login_required
@require_roles("superadmin", "admin")
def update_shop_config(shop_id: int):
    shop = db.session.get(Shop, shop_id)
    if not shop:
        return jsonify({"error": "shop_not_found"}), 404
    import json as _json
    body = request.get_json(force=True) or {}
    # 允许的字段：ocr_region(4-int array), unread_threshold(float), title_kw(str), auto_mode(bool), ai_model(str)
    cfg = {}
    if shop.config_json:
        try:
            cfg = _json.loads(shop.config_json)
        except Exception:
            cfg = {}
    for k in ["ocr_region", "unread_threshold", "title_kw", "auto_mode", "ai_model", "blacklist", "whitelist", "business_hours", "reply_delay"]:
        if k in body:
            cfg[k] = body[k]
    shop.config_json = _json.dumps(cfg, ensure_ascii=False)
    db.session.commit()
    return jsonify({"ok": True, "config": cfg})


@api_bp.get("/shops/ocr_templates")
@login_required
def get_ocr_templates():
    """获取 OCR 区域预设模板"""
    templates = [
        {
            "name": "1920×1080 (标准)",
            "description": "1920×1080 分辨率，适合大多数显示器",
            "ocr_region": [800, 200, 600, 300],
            "chat_region": [800, 200, 600, 400],
            "unread_threshold": 0.02
        },
        {
            "name": "1366×768 (笔记本)",
            "description": "1366×768 分辨率，适合笔记本屏幕",
            "ocr_region": [780, 180, 520, 360],
            "chat_region": [780, 180, 520, 450],
            "unread_threshold": 0.04
        },
        {
            "name": "2560×1440 (2K)",
            "description": "2560×1440 分辨率，适合高分辨率显示器",
            "ocr_region": [1100, 250, 800, 400],
            "chat_region": [1100, 250, 800, 500],
            "unread_threshold": 0.03
        },
        {
            "name": "3840×2160 (4K)",
            "description": "3840×2160 分辨率，适合4K显示器",
            "ocr_region": [1600, 350, 1200, 600],
            "chat_region": [1600, 350, 1200, 800],
            "unread_threshold": 0.025
        },
        {
            "name": "1440×900 (MacBook)",
            "description": "1440×900 分辨率，适合MacBook Air",
            "ocr_region": [600, 150, 400, 280],
            "chat_region": [600, 150, 400, 350],
            "unread_threshold": 0.035
        },
        {
            "name": "自定义",
            "description": "手动设置区域坐标",
            "ocr_region": [0, 0, 300, 300],
            "chat_region": [0, 0, 300, 300],
            "unread_threshold": 0.02
        }
    ]
    return jsonify(templates)


