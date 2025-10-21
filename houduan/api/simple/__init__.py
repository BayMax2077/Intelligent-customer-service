"""
简化版API模块
用于在SQLAlchemy连接问题期间提供基本功能
"""

from flask import Blueprint

# 创建简化版API蓝图
api_bp = Blueprint("api_simple", __name__)

# 导入所有简化版API模块
from . import auth, users, shops, kb, messages, statistics  # noqa: E402,F401

__all__ = ['api_bp', 'auth', 'users', 'shops', 'kb', 'messages', 'statistics']