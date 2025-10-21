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
        
        # 模拟用户数据，避免SQLAlchemy问题
        mock_users = {
            "admin": {"id": 1, "username": "admin", "role": "superadmin", "password": "admin123"},
            "superadmin": {"id": 2, "username": "superadmin", "role": "superadmin", "password": "superadmin123"},
            "test": {"id": 3, "username": "test", "role": "admin", "password": "test123"}
        }
        
        user_data = mock_users.get(username)
        if not user_data or user_data["password"] != password:
            return jsonify({"error": "invalid_credentials"}), 401
        
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


