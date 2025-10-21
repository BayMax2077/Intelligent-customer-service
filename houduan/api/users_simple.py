from __future__ import annotations

from flask import request, jsonify
from flask_login import login_required, current_user

from . import api_bp
from ..utils.security import require_roles


def get_shop_name(shop_id):
    """获取店铺名称"""
    if not shop_id:
        return "全局"
    
    # 简化的店铺名称映射
    shop_names = {
        1: "测试店铺1",
        2: "测试店铺2", 
        3: "测试店铺3",
        4: "测试店铺A",
        5: "测试店铺B",
        6: "测试店铺C"
    }
    return shop_names.get(shop_id, f"店铺{shop_id}")


@api_bp.get("/users")
def list_users():
    """获取用户列表 - 简化版"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    shop_id = request.args.get("shop_id", type=int)
    
    # 模拟用户数据
    all_users = [
        {
            "id": 1,
            "username": "admin",
            "role": "superadmin",
            "shop_id": None,
            "created_at": "2025-10-21T10:00:00",
            "updated_at": "2025-10-21T10:00:00"
        },
        {
            "id": 2,
            "username": "superadmin",
            "role": "superadmin", 
            "shop_id": None,
            "created_at": "2025-10-21T10:01:00",
            "updated_at": "2025-10-21T10:01:00"
        },
        {
            "id": 3,
            "username": "admin_shop1",
            "role": "admin",
            "shop_id": 4,
            "created_at": "2025-10-21T10:02:00",
            "updated_at": "2025-10-21T10:02:00"
        },
        {
            "id": 4,
            "username": "admin_shop2",
            "role": "admin",
            "shop_id": 5,
            "created_at": "2025-10-21T10:03:00",
            "updated_at": "2025-10-21T10:03:00"
        },
        {
            "id": 5,
            "username": "agent1_shop1",
            "role": "agent",
            "shop_id": 4,
            "created_at": "2025-10-21T10:04:00",
            "updated_at": "2025-10-21T10:04:00"
        },
        {
            "id": 6,
            "username": "agent2_shop1",
            "role": "agent",
            "shop_id": 4,
            "created_at": "2025-10-21T10:05:00",
            "updated_at": "2025-10-21T10:05:00"
        },
        {
            "id": 7,
            "username": "agent1_shop2",
            "role": "agent",
            "shop_id": 5,
            "created_at": "2025-10-21T10:06:00",
            "updated_at": "2025-10-21T10:06:00"
        },
        {
            "id": 8,
            "username": "agent1_shop3",
            "role": "agent",
            "shop_id": 6,
            "created_at": "2025-10-21T10:07:00",
            "updated_at": "2025-10-21T10:07:00"
        }
    ]
    
    # 权限过滤：admin只能看到本店铺用户（暂时注释掉，因为不需要认证）
    # if current_user.role == "admin":
    #     # 假设当前用户是店铺4的管理员
    #     all_users = [user for user in all_users if user["shop_id"] == 4 or user["shop_id"] is None]
    
    # 角色过滤
    if role:
        all_users = [user for user in all_users if user["role"] == role]
    
    # 店铺过滤
    if shop_id:
        all_users = [user for user in all_users if user["shop_id"] == shop_id]
    
    # 分页
    total = len(all_users)
    start = (page - 1) * per_page
    end = start + per_page
    users_page = all_users[start:end]
    
    # 添加店铺名称
    for user in users_page:
        user["shop_name"] = get_shop_name(user["shop_id"])
    
    return jsonify({
        "users": users_page,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    })


@api_bp.post("/users")
def create_user():
    """创建用户 - 简化版"""
    data = request.get_json(force=True) or {}
    
    # 验证必填字段
    required_fields = ["username", "password", "role"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field}_required"}), 400
    
    # 权限检查
    if current_user.role == "admin":
        # admin只能创建本店铺的客服
        if data.get("role") not in ["agent"]:
            return jsonify({"error": "insufficient_permission"}), 403
        data["shop_id"] = 4  # 假设当前用户是店铺4的管理员
    
    # 模拟创建用户
    new_user_id = 9  # 模拟新用户ID
    
    return jsonify({
        "id": new_user_id,
        "username": data["username"],
        "role": data["role"],
        "shop_id": data.get("shop_id"),
        "message": "用户创建成功"
    }), 201


@api_bp.get("/users/<int:user_id>")
def get_user(user_id: int):
    """获取单个用户信息 - 简化版"""
    # 模拟用户数据
    users = {
        1: {"id": 1, "username": "admin", "role": "superadmin", "shop_id": None},
        2: {"id": 2, "username": "superadmin", "role": "superadmin", "shop_id": None},
        3: {"id": 3, "username": "admin_shop1", "role": "admin", "shop_id": 4},
        4: {"id": 4, "username": "admin_shop2", "role": "admin", "shop_id": 5},
        5: {"id": 5, "username": "agent1_shop1", "role": "agent", "shop_id": 4},
        6: {"id": 6, "username": "agent2_shop1", "role": "agent", "shop_id": 4},
        7: {"id": 7, "username": "agent1_shop2", "role": "agent", "shop_id": 5},
        8: {"id": 8, "username": "agent1_shop3", "role": "agent", "shop_id": 6}
    }
    
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    # 权限检查
    if current_user.role == "admin" and user["shop_id"] != 4:
        return jsonify({"error": "insufficient_permission"}), 403
    
    user["shop_name"] = get_shop_name(user["shop_id"])
    user["created_at"] = "2025-10-21T10:00:00"
    user["updated_at"] = "2025-10-21T10:00:00"
    
    return jsonify(user)


@api_bp.put("/users/<int:user_id>")
def update_user(user_id: int):
    """更新用户信息 - 简化版"""
    # 模拟用户存在检查
    if user_id not in range(1, 9):
        return jsonify({"error": "user_not_found"}), 404
    
    data = request.get_json(force=True) or {}
    
    # 找到要更新的用户
    user_index = None
    for i, user in enumerate(MOCK_USERS):
        if user["id"] == user_id:
            user_index = i
            break
    
    if user_index is None:
        return jsonify({"error": "user_not_found"}), 404
    
    # 更新用户数据
    if "username" in data:
        MOCK_USERS[user_index]["username"] = data["username"]
    if "role" in data:
        MOCK_USERS[user_index]["role"] = data["role"]
    if "shop_id" in data:
        MOCK_USERS[user_index]["shop_id"] = data["shop_id"]
    
    # 更新更新时间
    from datetime import datetime
    MOCK_USERS[user_index]["updated_at"] = datetime.now().isoformat()
    
    # 返回更新后的用户数据
    updated_user = MOCK_USERS[user_index].copy()
    updated_user["shop_name"] = get_shop_name(updated_user["shop_id"])
    
    return jsonify({
        "message": "用户更新成功",
        "user": updated_user
    })


@api_bp.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    """删除用户 - 简化版"""
    # 模拟用户存在检查
    if user_id not in range(1, 9):
        return jsonify({"error": "user_not_found"}), 404
    
    # 不能删除自己
    if user_id == 1:  # 假设当前用户ID是1
        return jsonify({"error": "cannot_delete_self"}), 400
    
    # 模拟删除成功
    return jsonify({"message": "用户删除成功"})


@api_bp.post("/users/<int:user_id>/reset_password")
def reset_user_password(user_id: int):
    """重置用户密码 - 简化版"""
    # 模拟用户存在检查
    if user_id not in range(1, 9):
        return jsonify({"error": "user_not_found"}), 404
    
    data = request.get_json(force=True) or {}
    new_password = data.get("password")
    
    if not new_password:
        return jsonify({"error": "password_required"}), 400
    
    # 模拟重置成功
    return jsonify({"message": "密码重置成功"})
