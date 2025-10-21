"""
数据库健康检查服务
监控数据库连接状态，提供健康检查功能
"""

from __future__ import annotations

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import current_app
from loguru import logger

from ..utils.db_manager import db_manager, get_database_url
from ..utils.context_manager import context_manager


class DatabaseHealthMonitor:
    """数据库健康监控器"""
    
    def __init__(self):
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._health_history: List[Dict[str, Any]] = []
        self._max_history = 100
        self._check_interval = 30  # 30秒检查一次
        self._alert_threshold = 3  # 连续3次失败才报警
        
    def start_monitoring(self, app):
        """开始监控数据库健康状态"""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(app,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("数据库健康监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("数据库健康监控已停止")
    
    def _monitor_loop(self, app):
        """监控循环"""
        consecutive_failures = 0
        
        while self._monitoring:
            try:
                with context_manager.app_context(app):
                    health_info = db_manager.health_check(get_database_url())
                    
                    # 记录健康状态
                    self._record_health_status(health_info)
                    
                    # 检查是否需要报警
                    if health_info['status'] == 'healthy':
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        if consecutive_failures >= self._alert_threshold:
                            self._send_alert(health_info, consecutive_failures)
                    
            except Exception as e:
                logger.error(f"数据库健康监控错误: {e}")
                consecutive_failures += 1
                if consecutive_failures >= self._alert_threshold:
                    self._send_alert({'status': 'error', 'error': str(e)}, consecutive_failures)
            
            time.sleep(self._check_interval)
    
    def _record_health_status(self, health_info: Dict[str, Any]):
        """记录健康状态"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'status': health_info['status'],
            'response_time': health_info.get('response_time', 0),
            'error': health_info.get('error')
        }
        
        self._health_history.append(record)
        
        # 保持历史记录在限制范围内
        if len(self._health_history) > self._max_history:
            self._health_history = self._health_history[-self._max_history:]
    
    def _send_alert(self, health_info: Dict[str, Any], consecutive_failures: int):
        """发送健康警报"""
        alert_message = f"数据库健康检查连续失败 {consecutive_failures} 次"
        if health_info.get('error'):
            alert_message += f": {health_info['error']}"
        
        logger.warning(alert_message)
        
        # 这里可以添加更多的警报机制，比如发送邮件、短信等
        # 目前只记录日志
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取当前健康状态"""
        if not self._health_history:
            return {'status': 'unknown', 'message': '没有健康检查历史'}
        
        latest = self._health_history[-1]
        
        # 计算统计信息
        recent_records = self._health_history[-10:]  # 最近10次检查
        healthy_count = sum(1 for r in recent_records if r['status'] == 'healthy')
        total_count = len(recent_records)
        
        avg_response_time = sum(r.get('response_time', 0) for r in recent_records) / total_count if total_count > 0 else 0
        
        return {
            'current_status': latest['status'],
            'current_timestamp': latest['timestamp'],
            'current_response_time': latest.get('response_time', 0),
            'current_error': latest.get('error'),
            'recent_health_rate': healthy_count / total_count if total_count > 0 else 0,
            'avg_response_time': avg_response_time,
            'total_checks': len(self._health_history),
            'monitoring_active': self._monitoring
        }
    
    def get_health_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取健康检查历史"""
        return self._health_history[-limit:] if limit > 0 else self._health_history


# 全局数据库健康监控器
db_health_monitor = DatabaseHealthMonitor()


def start_db_health_monitoring(app):
    """启动数据库健康监控"""
    db_health_monitor.start_monitoring(app)


def stop_db_health_monitoring():
    """停止数据库健康监控"""
    db_health_monitor.stop_monitoring()


def get_db_health_status() -> Dict[str, Any]:
    """获取数据库健康状态"""
    return db_health_monitor.get_health_status()


def get_db_health_history(limit: int = 20) -> List[Dict[str, Any]]:
    """获取数据库健康历史"""
    return db_health_monitor.get_health_history(limit)
