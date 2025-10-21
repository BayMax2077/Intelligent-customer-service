from __future__ import annotations

from flask import Blueprint

api_bp = Blueprint("api", __name__)

# 子路由注册 - 临时只导入不依赖SQLAlchemy的模块
from . import auth, users_simple as users, shops, messages, audit, statistics, kb, import_tasks  # noqa: E402,F401


