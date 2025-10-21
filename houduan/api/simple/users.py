"""
简化版用户管理API
使用模拟数据，避免SQLAlchemy依赖
"""

from __future__ import annotations

from datetime import datetime
from flask import request, jsonify
from werkzeug.security import generate_password_hash

from . import api_bp

# 模拟用户数据
MOCK_USERS = [
    {"id": 1, "username": "admin", "role": "superadmin", "shop_id": None, "password_hash": generate_password_hash("admin123"), "created_at": "2025-10-21T10:00:00", "updated_at": "2025-10-21T10:00:00"},
    {"id": 2, "username": "superadmin", "role": "superadmin", "shop_id": None, "password_hash": generate_password_hash("superadmin123"), "created_at": "2025-10-21T10:01:00", "updated_at": "2025-10-21T10:01:00"},
    {"id": 3, "username": "admin_shop1", "role": "admin", "shop_id": 1, "password_hash": generate_password_hash("admin123"), "created_at": "2025-10-21T10:02:00", "updated_at": "2025-10-21T10:02:00"},
    {"id": 4, "username": "admin_shop2", "role": "admin", "shop_id": 2, "password_hash": generate_password_hash("admin123"), "created_at": "2025-10-21T10:03:00", "updated_at": "2025-10-21T10:03:00"},
    {"id": 5, "username": "agent1_shop1", "role": "agent", "shop_id": 1, "password_hash": generate_password_hash("agent123"), "created_at": "2025-10-21T10:04:00", "updated_at": "2025-10-21T10:04:00"},
    {"id": 6, "username": "agent2_shop1", "role": "agent", "shop_id": 1, "password_hash": generate_password_hash("agent123"), "created_at": "2025-10-21T10:05:00", "updated_at": "2025-10-21T10:05:00"},
    {"id": 7, "username": "agent1_shop2", "role": "agent", "shop_id": 2, "password_hash": generate_password_hash("agent123"), "created_at": "2025-10-21T10:06:00", "updated_at": "2025-10-21T10:06:00"},
    {"id": 8, "username": "agent1_shop3", "role": "agent", "shop_id": 3, "password_hash": generate_password_hash("agent123"), "created_at": "2025-10-21T10:07:00", "updated_at": "2025-10-21T10:07:00"}
]

# 模拟店铺数据
MOCK_SHOPS = {
    1: {"id": 1, "name": "测试店铺A"},
    2: {"id": 2, "name": "测试店铺B"},
    3: {"id": 3, "name": "测试店铺C"},
    4: {"id": 4, "name": "测试店铺D"},
}

def get_shop_name(shop_id):
    """获取店铺名称"""
    if not shop_id:
        return "全局"
    return MOCK_SHOPS.get(shop_id, {}).get("name", f"未知店铺{shop_id}")


@api_bp.get("/users")
def list_users():
    """获取用户列表 - 简化版"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    shop_id = request.args.get("shop_id", type=int)

    all_users = []
    for user in MOCK_USERS:
        user_copy = user.copy()
        user_copy["shop_name"] = get_shop_name(user_copy["shop_id"])
        all_users.append(user_copy)
    
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
