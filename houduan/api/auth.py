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
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        # 从数据库获取用户数据
        try:
            # 为避免 Flask-SQLAlchemy 绑定问题，这里走轻量的原生查询
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
        # 将真实错误返回，便于前端显示定位（仅本地环境）
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api_bp.post("/auth/logout")
def logout():
    logout_user()
    return jsonify({"ok": True})


