"""
应用上下文管理器
解决SQLAlchemy应用上下文问题
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Optional, Any, Callable
from flask import current_app, has_app_context
from flask_sqlalchemy import SQLAlchemy
from loguru import logger


class AppContextManager:
    """应用上下文管理器"""
    
    def __init__(self):
        self._contexts: dict = {}
        self._lock = threading.Lock()
    
    @contextmanager
    def app_context(self, app=None):
        """应用上下文管理器"""
        if app is None:
            if has_app_context():
                yield current_app
                return
            else:
                raise RuntimeError("没有可用的Flask应用上下文")
        
        with app.app_context():
            yield app
    
    def safe_db_operation(self, operation: Callable, *args, **kwargs):
        """安全的数据库操作"""
        try:
            if has_app_context():
                return operation(*args, **kwargs)
            else:
                logger.warning("没有应用上下文，跳过数据库操作")
                return None
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            raise
    
    def ensure_app_context(self, app, operation: Callable, *args, **kwargs):
        """确保应用上下文的数据库操作"""
        try:
            with self.app_context(app):
                return operation(*args, **kwargs)
        except Exception as e:
            logger.error(f"应用上下文数据库操作失败: {e}")
            raise


# 全局应用上下文管理器
context_manager = AppContextManager()


def with_app_context(app):
    """装饰器：确保函数在应用上下文中执行"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                with context_manager.app_context(app):
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"应用上下文装饰器错误: {e}")
                raise
        return wrapper
    return decorator


def safe_db_query(query_func, *args, **kwargs):
    """安全的数据库查询"""
    try:
        if has_app_context():
            return query_func(*args, **kwargs)
        else:
            logger.warning("没有应用上下文，返回空结果")
            return []
    except Exception as e:
        logger.error(f"数据库查询失败: {e}")
        return []


def safe_db_commit(commit_func, *args, **kwargs):
    """安全的数据库提交"""
    try:
        if has_app_context():
            return commit_func(*args, **kwargs)
        else:
            logger.warning("没有应用上下文，跳过数据库提交")
            return False
    except Exception as e:
        logger.error(f"数据库提交失败: {e}")
        return False
