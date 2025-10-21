"""
数据库连接池管理器
提供连接池配置、监控和优化功能
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.engine import Engine
from loguru import logger

from .db_manager import get_database_url


class ConnectionPoolMonitor:
    """连接池监控器"""
    
    def __init__(self):
        self._pool_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self, engine: Engine, pool_name: str = "default"):
        """开始监控连接池"""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(engine, pool_name),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"连接池监控已启动: {pool_name}")
    
    def stop_monitoring(self):
        """停止监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("连接池监控已停止")
    
    def _monitor_loop(self, engine: Engine, pool_name: str):
        """监控循环"""
        while self._monitoring:
            try:
                pool = engine.pool
                stats = {
                    'timestamp': datetime.now().isoformat(),
                    'size': getattr(pool, 'size', lambda: 0)(),
                    'checked_in': getattr(pool, 'checkedin', lambda: 0)(),
                    'checked_out': getattr(pool, 'checkedout', lambda: 0)(),
                    'overflow': getattr(pool, 'overflow', lambda: 0)(),
                    'invalid': getattr(pool, 'invalid', lambda: 0)()
                }
                
                with self._lock:
                    self._pool_stats[pool_name] = stats
                
                # 检查连接池健康状态
                self._check_pool_health(pool_name, stats)
                
            except Exception as e:
                logger.error(f"连接池监控错误: {e}")
            
            time.sleep(30)  # 30秒监控一次
    
    def _check_pool_health(self, pool_name: str, stats: Dict[str, Any]):
        """检查连接池健康状态"""
        # 检查连接池使用率
        total_connections = stats['size'] + stats['overflow']
        if total_connections > 0:
            usage_rate = stats['checked_out'] / total_connections
            if usage_rate > 0.8:
                logger.warning(f"连接池 {pool_name} 使用率过高: {usage_rate:.2%}")
        
        # 检查无效连接
        if stats['invalid'] > 0:
            logger.warning(f"连接池 {pool_name} 有 {stats['invalid']} 个无效连接")
    
    def get_pool_stats(self, pool_name: str = None) -> Dict[str, Any]:
        """获取连接池统计信息"""
        with self._lock:
            if pool_name:
                return self._pool_stats.get(pool_name, {})
            return self._pool_stats.copy()
    
    def get_pool_health_report(self) -> Dict[str, Any]:
        """获取连接池健康报告"""
        with self._lock:
            if not self._pool_stats:
                return {'status': 'no_data', 'message': '没有连接池数据'}
            
            total_pools = len(self._pool_stats)
            healthy_pools = 0
            
            for pool_name, stats in self._pool_stats.items():
                total_connections = stats['size'] + stats['overflow']
                if total_connections > 0:
                    usage_rate = stats['checked_out'] / total_connections
                    if usage_rate < 0.8 and stats['invalid'] == 0:
                        healthy_pools += 1
            
            health_rate = healthy_pools / total_pools if total_pools > 0 else 0
            
            return {
                'total_pools': total_pools,
                'healthy_pools': healthy_pools,
                'health_rate': health_rate,
                'status': 'healthy' if health_rate > 0.8 else 'warning' if health_rate > 0.5 else 'critical',
                'pools': self._pool_stats
            }


class ConnectionPoolManager:
    """连接池管理器"""
    
    def __init__(self):
        self._engines: Dict[str, Engine] = {}
        self._monitors: Dict[str, ConnectionPoolMonitor] = {}
        self._lock = threading.Lock()
        
    def create_optimized_pool(self, database_url: str, pool_name: str = "default") -> Engine:
        """创建优化的连接池"""
        with self._lock:
            if pool_name in self._engines:
                return self._engines[pool_name]
            
            try:
                # 根据数据库类型选择连接池配置
                if database_url.startswith('sqlite'):
                    # SQLite使用静态连接池
                    engine = create_engine(
                        database_url,
                        poolclass=StaticPool,
                        connect_args={'check_same_thread': False},
                        echo=False
                    )
                else:
                    # 其他数据库使用队列连接池
                    engine = create_engine(
                        database_url,
                        poolclass=QueuePool,
                        pool_size=10,          # 基础连接数
                        max_overflow=20,       # 最大溢出连接数
                        pool_pre_ping=True,    # 连接前检查
                        pool_recycle=3600,     # 1小时回收连接
                        pool_timeout=30,       # 获取连接超时
                        echo=False
                    )
                
                # 添加连接池事件监听器
                self._add_pool_listeners(engine, pool_name)
                
                self._engines[pool_name] = engine
                
                # 启动连接池监控
                monitor = ConnectionPoolMonitor()
                monitor.start_monitoring(engine, pool_name)
                self._monitors[pool_name] = monitor
                
                logger.info(f"连接池创建成功: {pool_name}")
                return engine
                
            except Exception as e:
                logger.error(f"创建连接池失败: {e}")
                raise
    
    def _add_pool_listeners(self, engine: Engine, pool_name: str):
        """添加连接池事件监听器"""
        
        @event.listens_for(engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            logger.debug(f"连接池 {pool_name}: 新连接建立")
        
        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug(f"连接池 {pool_name}: 连接被检出")
        
        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            logger.debug(f"连接池 {pool_name}: 连接被检入")
        
        @event.listens_for(engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            logger.warning(f"连接池 {pool_name}: 连接失效 - {exception}")
    
    def get_engine(self, pool_name: str = "default") -> Optional[Engine]:
        """获取连接池引擎"""
        with self._lock:
            return self._engines.get(pool_name)
    
    def close_pool(self, pool_name: str):
        """关闭连接池"""
        with self._lock:
            if pool_name in self._engines:
                try:
                    # 停止监控
                    if pool_name in self._monitors:
                        self._monitors[pool_name].stop_monitoring()
                        del self._monitors[pool_name]
                    
                    # 关闭引擎
                    self._engines[pool_name].dispose()
                    del self._engines[pool_name]
                    
                    logger.info(f"连接池已关闭: {pool_name}")
                except Exception as e:
                    logger.error(f"关闭连接池失败: {e}")
    
    def close_all_pools(self):
        """关闭所有连接池"""
        with self._lock:
            for pool_name in list(self._engines.keys()):
                self.close_pool(pool_name)
    
    def get_pool_health_report(self) -> Dict[str, Any]:
        """获取所有连接池健康报告"""
        report = {
            'total_pools': len(self._engines),
            'pools': {}
        }
        
        for pool_name, monitor in self._monitors.items():
            report['pools'][pool_name] = monitor.get_pool_health_report()
        
        return report
    
    def optimize_pool_config(self, pool_name: str) -> Dict[str, Any]:
        """优化连接池配置建议"""
        monitor = self._monitors.get(pool_name)
        if not monitor:
            return {'error': '连接池监控器不存在'}
        
        stats = monitor.get_pool_stats(pool_name)
        if not stats:
            return {'error': '没有连接池统计数据'}
        
        suggestions = []
        
        # 分析连接池使用情况
        total_connections = stats['size'] + stats['overflow']
        if total_connections > 0:
            usage_rate = stats['checked_out'] / total_connections
            
            if usage_rate > 0.9:
                suggestions.append({
                    'type': 'increase_pool_size',
                    'message': '连接池使用率过高，建议增加连接池大小',
                    'priority': 'high'
                })
            elif usage_rate < 0.1:
                suggestions.append({
                    'type': 'decrease_pool_size',
                    'message': '连接池使用率过低，建议减少连接池大小',
                    'priority': 'medium'
                })
        
        # 检查无效连接
        if stats['invalid'] > 0:
            suggestions.append({
                'type': 'check_connections',
                'message': f'发现 {stats["invalid"]} 个无效连接，建议检查连接配置',
                'priority': 'high'
            })
        
        return {
            'pool_name': pool_name,
            'current_stats': stats,
            'suggestions': suggestions,
            'optimization_score': self._calculate_optimization_score(stats)
        }
    
    def _calculate_optimization_score(self, stats: Dict[str, Any]) -> int:
        """计算连接池优化分数"""
        if not stats:
            return 0
        
        score = 100
        
        # 基于使用率调整分数
        total_connections = stats['size'] + stats['overflow']
        if total_connections > 0:
            usage_rate = stats['checked_out'] / total_connections
            if usage_rate > 0.9:
                score -= 30
            elif usage_rate < 0.1:
                score -= 20
        
        # 基于无效连接调整分数
        if stats['invalid'] > 0:
            score -= stats['invalid'] * 10
        
        return max(0, min(100, score))


# 全局连接池管理器
pool_manager = ConnectionPoolManager()


def get_optimized_engine(database_url: str, pool_name: str = "default") -> Engine:
    """获取优化的数据库引擎"""
    return pool_manager.create_optimized_pool(database_url, pool_name)


def get_pool_health_report() -> Dict[str, Any]:
    """获取连接池健康报告"""
    return pool_manager.get_pool_health_report()


def optimize_connection_pools() -> Dict[str, Any]:
    """优化连接池配置"""
    report = {
        'optimization_results': {},
        'overall_score': 0
    }
    
    total_score = 0
    pool_count = 0
    
    for pool_name in pool_manager._engines.keys():
        optimization = pool_manager.optimize_pool_config(pool_name)
        report['optimization_results'][pool_name] = optimization
        
        if 'optimization_score' in optimization:
            total_score += optimization['optimization_score']
            pool_count += 1
    
    if pool_count > 0:
        report['overall_score'] = total_score / pool_count
    
    return report
