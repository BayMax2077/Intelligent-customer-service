from __future__ import annotations

from flask import request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from . import api_bp
from ..app import db
from ..models import User, Shop
from ..utils.security import require_roles


def get_shop_name(shop_id):
    """获取店铺名称"""
    if not shop_id:
        return "全局"
    shop = db.session.get(Shop, shop_id)
    return shop.name if shop else "未知店铺"


@api_bp.get("/users")
@login_required
@require_roles("superadmin", "admin")
def list_users():
    """获取用户列表"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    shop_id = request.args.get("shop_id", type=int)
    
    query = User.query
    
    # 权限过滤：admin只能看到本店铺用户
    if current_user.role == "admin":
        query = query.filter(User.shop_id == current_user.shop_id)
    
    if role:
        query = query.filter(User.role == role)
    if shop_id:
        query = query.filter(User.shop_id == shop_id)
    
    users = query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "shop_id": user.shop_id,
                "shop_name": get_shop_name(user.shop_id),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            }
            for user in users.items
        ],
        "total": users.total,
        "page": page,
        "per_page": per_page,
        "pages": users.pages,
    })


@api_bp.post("/users")
@login_required
@require_roles("superadmin", "admin")
def create_user():
    """创建用户"""
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
        data["shop_id"] = current_user.shop_id
    
    # 检查用户名是否已存在
    if db.session.query(User).filter_by(username=data["username"]).first():
        return jsonify({"error": "username_exists"}), 400
    
    # 创建用户
    user = User(
        username=data["username"],
        password_hash=generate_password_hash(data["password"]),
        role=data["role"],
        shop_id=data.get("shop_id")
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "id": user.id,
        "message": "用户创建成功"
    }), 201


@api_bp.get("/users/<int:user_id>")
@login_required
@require_roles("superadmin", "admin")
def get_user(user_id: int):
    """获取单个用户信息"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    # 权限检查
    if current_user.role == "admin" and user.shop_id != current_user.shop_id:
        return jsonify({"error": "insufficient_permission"}), 403
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "shop_id": user.shop_id,
        "shop_name": get_shop_name(user.shop_id),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    })


@api_bp.put("/users/<int:user_id>")
@login_required
@require_roles("superadmin", "admin")
def update_user(user_id: int):
    """更新用户信息"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    # 权限检查
    if current_user.role == "admin" and user.shop_id != current_user.shop_id:
        return jsonify({"error": "insufficient_permission"}), 403
    
    data = request.get_json(force=True) or {}
    
    # 更新字段
    if "username" in data:
        # 检查用户名是否已存在
        existing = db.session.query(User).filter(User.username == data["username"], User.id != user_id).first()
        if existing:
            return jsonify({"error": "username_exists"}), 400
        user.username = data["username"]
    
    if "password" in data and data["password"]:
        user.password_hash = generate_password_hash(data["password"])
    
    if "role" in data:
        # 权限检查
        if current_user.role == "admin" and data["role"] not in ["agent"]:
            return jsonify({"error": "insufficient_permission"}), 403
        user.role = data["role"]
    
    if "shop_id" in data:
        # 权限检查
        if current_user.role == "admin":
            return jsonify({"error": "insufficient_permission"}), 403
        user.shop_id = data["shop_id"]
    
    db.session.commit()
    
    return jsonify({"message": "用户更新成功"})


@api_bp.delete("/users/<int:user_id>")
@login_required
@require_roles("superadmin")
def delete_user(user_id: int):
    """删除用户"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    # 不能删除自己
    if user.id == current_user.id:
        return jsonify({"error": "cannot_delete_self"}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "用户删除成功"})


@api_bp.post("/users/<int:user_id>/reset_password")
@login_required
@require_roles("superadmin", "admin")
def reset_user_password(user_id: int):
    """重置用户密码"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    
    # 权限检查
    if current_user.role == "admin" and user.shop_id != current_user.shop_id:
        return jsonify({"error": "insufficient_permission"}), 403
    
    data = request.get_json(force=True) or {}
    new_password = data.get("password")
    
    if not new_password:
        return jsonify({"error": "password_required"}), 400
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({"message": "密码重置成功"})


def get_shop_name(shop_id: int) -> str:
    """获取店铺名称"""
    if not shop_id:
        return "全局"
    
    shop = db.session.get(Shop, shop_id)
    return shop.name if shop else f"店铺{shop_id}"
