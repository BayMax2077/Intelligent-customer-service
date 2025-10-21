"""
安全与鉴权相关工具

提供: 密码哈希/校验, 角色检查装饰器
"""

from __future__ import annotations

import functools
from typing import Callable

from werkzeug.security import check_password_hash, generate_password_hash
from flask import abort
from flask_login import current_user


def hash_password(plain: str) -> str:
    return generate_password_hash(plain)


def verify_password(pw_hash: str, plain: str) -> bool:
    return check_password_hash(pw_hash, plain)


def require_roles(*roles: str) -> Callable:
    """要求当前用户具备任一给定角色。"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if roles and getattr(current_user, "role", None) not in roles:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


