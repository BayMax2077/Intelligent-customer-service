"""
简化版认证API
使用模拟数据，避免SQLAlchemy依赖
"""

from __future__ import annotations

from flask import request, jsonify
from flask_login import UserMixin, login_user, logout_user

from . import api_bp


class LoginUser(UserMixin):
    def __init__(self, user):
        self._user = user

    @property
    def id(self) -> str:  # type: ignore[override]
        return str(self._user.id)

    @property
    def role(self) -> str:
        return self._user.role


@api_bp.post("/auth/login")
def login():
    """用户登录 - 简化版"""
    try:
        data = request.get_json(force=True)
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        # 验证输入是否为空
        if not username or not password:
            return jsonify({"error": "请输入用户名和密码"}), 400
        
        # 从数据库获取用户数据（避免依赖 Flask-SQLAlchemy 绑定）
        try:
            from flask import current_app
            from sqlalchemy import create_engine, text
            from werkzeug.security import check_password_hash
            database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
            engine = create_engine(database_url)
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id, username, password_hash, role FROM users WHERE username = :u LIMIT 1"),
                    {"u": username},
                ).mappings().first()
            if not row or not check_password_hash(row["password_hash"], password):
                return jsonify({"error": "invalid_credentials"}), 401
            
            user_data = {"id": row["id"], "username": row["username"], "role": row["role"]}
        except Exception as e:
            # 数据库查询失败
            return jsonify({"error": "database_error", "detail": str(e)}), 500
        
        # 创建模拟用户对象
        class MockUser:
            def __init__(self, data):
                self.id = data["id"]
                self.username = data["username"]
                self.role = data["role"]
        
        mock_user = MockUser(user_data)
        login_user(LoginUser(mock_user))
        return jsonify({"ok": True, "user": {"id": mock_user.id, "username": mock_user.username, "role": mock_user.role}})
    except Exception as e:
        # 生产环境不暴露详细错误，开发环境可以打印日志
        import traceback
        traceback.print_exc()
        return jsonify({"error": "登录服务异常，请稍后重试"}), 500


@api_bp.post("/auth/logout")
def logout():
    """用户登出 - 简化版"""
    logout_user()
    return jsonify({"ok": True})
