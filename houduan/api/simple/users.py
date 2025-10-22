"""
简化版用户管理API
使用模拟数据，避免SQLAlchemy依赖
"""

from __future__ import annotations

from datetime import datetime
from flask import request, jsonify
from werkzeug.security import generate_password_hash

from . import api_bp

# 数据库查询函数
def get_users_from_db():
    """从数据库获取用户列表"""
    try:
        from ..app import db
        from ..models import User, Shop
        users = User.query.all()
        result = []
        for user in users:
            shop_name = None
            if user.shop_id:
                shop = Shop.query.get(user.shop_id)
                shop_name = shop.name if shop else f"未知店铺{user.shop_id}"
            
            result.append({
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "shop_id": user.shop_id,
                "shop_name": shop_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            })
        return result
    except Exception:
        return []

def get_shop_name(shop_id):
    """获取店铺名称"""
    if not shop_id:
        return "全局"
    try:
        from ..app import db
        from ..models import Shop
        shop = Shop.query.get(shop_id)
        return shop.name if shop else f"未知店铺{shop_id}"
    except Exception:
        return f"未知店铺{shop_id}"


@api_bp.get("/users")
def list_users():
    """获取用户列表 - 简化版"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    shop_id = request.args.get("shop_id", type=int)

    all_users = get_users_from_db()
    
    # 角色过滤
    if role:
        all_users = [user for user in all_users if user["role"] == role]
    
    # 店铺过滤
    if shop_id:
        all_users = [user for user in all_users if user["shop_id"] == shop_id]

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = all_users[start:end]

    return jsonify({
        "users": paginated_users,
        "total": len(all_users),
        "page": page,
        "per_page": per_page,
        "pages": (len(all_users) + per_page - 1) // per_page,
    })


@api_bp.post("/users")
def create_user():
    """创建用户 - 简化版"""
    data = request.get_json(force=True) or {}
    
    required_fields = ["username", "password", "role"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field}_required"}), 400
    
    if any(user["username"] == data["username"] for user in MOCK_USERS):
        return jsonify({"error": "username_exists"}), 400
    
    new_id = max(user["id"] for user in MOCK_USERS) + 1 if MOCK_USERS else 1
    new_user = {
        "id": new_id,
        "username": data["username"],
        "password_hash": generate_password_hash(data["password"]),
        "role": data["role"],
        "shop_id": data.get("shop_id"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    MOCK_USERS.append(new_user)
    
    return jsonify({
        "id": new_user["id"],
        "message": "用户创建成功"
    }), 201


@api_bp.get("/users/<int:user_id>")
def get_user(user_id):
    """获取单个用户 - 简化版"""
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    user_copy = user.copy()
    user_copy["shop_name"] = get_shop_name(user_copy["shop_id"])
    user_copy.pop("password_hash", None) # Don't expose password hash
    return jsonify(user_copy)


@api_bp.put("/users/<int:user_id>")
def update_user(user_id: int):
    """更新用户信息 - 简化版"""
    data = request.get_json(force=True) or {}
    user_index = None
    for i, user in enumerate(MOCK_USERS):
        if user["id"] == user_id:
            user_index = i
            break
    
    if user_index is None:
        return jsonify({"error": "user_not_found"}), 404
    
    if "username" in data:
        MOCK_USERS[user_index]["username"] = data["username"]
    if "role" in data:
        MOCK_USERS[user_index]["role"] = data["role"]
    if "shop_id" in data:
        MOCK_USERS[user_index]["shop_id"] = data["shop_id"]
    
    MOCK_USERS[user_index]["updated_at"] = datetime.now().isoformat()
    
    updated_user = MOCK_USERS[user_index].copy()
    updated_user["shop_name"] = get_shop_name(updated_user["shop_id"])
    
    return jsonify({
        "message": "用户更新成功",
        "user": updated_user
    })


@api_bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    """删除用户 - 简化版"""
    global MOCK_USERS
    initial_len = len(MOCK_USERS)
    MOCK_USERS = [user for user in MOCK_USERS if user["id"] != user_id]
    if len(MOCK_USERS) == initial_len:
        return jsonify({"error": "user_not_found"}), 404
    return jsonify({"message": "用户删除成功"})


@api_bp.post("/users/<int:user_id>/reset_password")
def reset_password(user_id):
    """重置用户密码 - 简化版"""
    data = request.get_json(force=True) or {}
    new_password = data.get("new_password")
    if not new_password:
        return jsonify({"error": "new_password_required"}), 400
    
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    user["password_hash"] = generate_password_hash(new_password)
    user["updated_at"] = datetime.now().isoformat()
    
    return jsonify({"message": "密码重置成功"})
