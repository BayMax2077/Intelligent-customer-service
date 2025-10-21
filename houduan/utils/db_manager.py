"""
数据库连接管理器
解决SQLAlchemy连接问题，提供稳定的数据库访问
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from loguru import logger

# 导入优化模块
try:
    from .connection_pool import pool_manager, get_optimized_engine
    from .cache_manager import cache_manager, cached
    from .query_optimizer import query_optimizer, optimize_query
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    logger.warning("优化模块不可用，将使用基础功能")


class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self._engines: Dict[str, Engine] = {}
        self._connections: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._health_check_cache: Dict[str, Dict[str, Any]] = {}
        self._retry_count = 3
        self._retry_delay = 1.0
        
    def get_engine(self, database_url: str, pool_size: int = 5, max_overflow: int = 10) -> Engine:
        """获取数据库引擎，支持连接池"""
        with self._lock:
            if database_url not in self._engines:
                try:
                    # 如果优化模块可用，使用优化的连接池
                    if OPTIMIZATION_AVAILABLE:
                        engine = get_optimized_engine(database_url, "main")
                        self._engines[database_url] = engine
                        logger.info(f"优化数据库引擎创建成功: {database_url}")
                        return engine
                    
                    # 回退到基础配置
                    engine_config = {
                        'echo': False,
                    }
                    
                    # 如果是SQLite，使用特殊配置
                    if database_url.startswith('sqlite'):
                        engine_config.update({
                            'poolclass': StaticPool,
                            'connect_args': {'check_same_thread': False}
                        })
                    else:
                        # 非SQLite数据库使用连接池
                        engine_config.update({
                            'pool_size': pool_size,
                            'max_overflow': max_overflow,
                            'pool_pre_ping': True,  # 连接前检查
                            'pool_recycle': 3600,   # 1小时回收连接
                        })
                    
                    engine = create_engine(database_url, **engine_config)
                    
                    # 添加连接事件监听器
                    @event.listens_for(engine, "connect")
                    def set_sqlite_pragma(dbapi_connection, connection_record):
                        if database_url.startswith('sqlite'):
                            cursor = dbapi_connection.cursor()
                            cursor.execute("PRAGMA foreign_keys=ON")
                            cursor.close()
                    
                    self._engines[database_url] = engine
                    logger.info(f"数据库引擎创建成功: {database_url}")
                    
                except Exception as e:
                    logger.error(f"创建数据库引擎失败: {e}")
                    raise
                    
            return self._engines[database_url]
    
    def get_connection(self, database_url: str):
        """获取数据库连接"""
        engine = self.get_engine(database_url)
        try:
            connection = engine.connect()
            return connection
        except Exception as e:
            logger.error(f"获取数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_session(self, database_url: str):
        """获取数据库会话上下文管理器"""
        connection = None
        try:
            connection = self.get_connection(database_url)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def health_check(self, database_url: str) -> Dict[str, Any]:
        """数据库健康检查"""
        cache_key = database_url
        now = datetime.now()
        
        # 检查缓存（5分钟内有效）
        if cache_key in self._health_check_cache:
            cached_result = self._health_check_cache[cache_key]
            if now - cached_result['timestamp'] < timedelta(minutes=5):
                return cached_result['result']
        
        result = {
            'status': 'unknown',
            'response_time': 0,
            'error': None,
            'timestamp': now.isoformat()
        }
        
        try:
            start_time = datetime.now()
            with self.get_session(database_url) as session:
                # 执行简单查询测试连接
                session.execute(text("SELECT 1"))
                end_time = datetime.now()
                
                result.update({
                    'status': 'healthy',
                    'response_time': (end_time - start_time).total_seconds(),
                    'error': None
                })
                
        except Exception as e:
            result.update({
                'status': 'unhealthy',
                'error': str(e)
            })
            logger.warning(f"数据库健康检查失败: {e}")
        
        # 缓存结果
        self._health_check_cache[cache_key] = {
            'result': result,
            'timestamp': now
        }
        
        return result
    
    def retry_operation(self, operation, *args, **kwargs):
        """重试数据库操作"""
        last_exception = None
        
        for attempt in range(self._retry_count):
            try:
                return operation(*args, **kwargs)
            except (DisconnectionError, SQLAlchemyError) as e:
                last_exception = e
                if attempt < self._retry_count - 1:
                    logger.warning(f"数据库操作失败，重试 {attempt + 1}/{self._retry_count}: {e}")
                    import time
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    logger.error(f"数据库操作最终失败: {e}")
                    raise last_exception
            except Exception as e:
                logger.error(f"数据库操作非重试错误: {e}")
                raise e
        
        raise last_exception
    
    def close_all_connections(self):
        """关闭所有数据库连接"""
        with self._lock:
            for url, engine in self._engines.items():
                try:
                    engine.dispose()
                    logger.info(f"关闭数据库连接: {url}")
                except Exception as e:
                    logger.error(f"关闭数据库连接失败: {e}")
            self._engines.clear()
            self._connections.clear()
            self._health_check_cache.clear()


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_database_url() -> str:
    """获取数据库URL"""
    # 优先使用环境变量
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # 默认使用SQLite
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, '..', 'data', 'sqlite.db')
    return f'sqlite:///{os.path.abspath(db_path)}'


def init_database_manager(app) -> DatabaseManager:
    """初始化数据库管理器"""
    try:
        database_url = get_database_url()
        logger.info(f"初始化数据库管理器: {database_url}")
        
        # 测试连接
        health = db_manager.health_check(database_url)
        if health['status'] == 'healthy':
            logger.info("数据库连接健康")
        else:
            logger.warning(f"数据库连接异常: {health.get('error', 'unknown')}")
        
        return db_manager
        
    except Exception as e:
        logger.error(f"初始化数据库管理器失败: {e}")
        raise


def get_db_session():
    """获取数据库会话（用于Flask应用上下文）"""
    if not current_app:
        raise RuntimeError("必须在Flask应用上下文中使用")
    
    database_url = get_database_url()
    return db_manager.get_session(database_url)


def safe_db_operation(operation, *args, **kwargs):
    """安全的数据库操作，带重试机制"""
    return db_manager.retry_operation(operation, *args, **kwargs)
