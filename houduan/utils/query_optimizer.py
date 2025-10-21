"""
数据库查询优化器
提供查询性能优化、索引建议和查询分析功能
"""

from __future__ import annotations

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from flask import current_app
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from loguru import logger

from .db_manager import db_manager, get_database_url


class QueryProfiler:
    """查询性能分析器"""
    
    def __init__(self):
        self._queries: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._max_queries = 1000
        self._slow_query_threshold = 1.0  # 1秒
        
    def record_query(self, sql: str, duration: float, params: Dict = None):
        """记录查询性能"""
        with self._lock:
            query_info = {
                'timestamp': datetime.now().isoformat(),
                'sql': sql,
                'duration': duration,
                'params': params or {},
                'is_slow': duration > self._slow_query_threshold
            }
            
            self._queries.append(query_info)
            
            # 保持查询记录在限制范围内
            if len(self._queries) > self._max_queries:
                self._queries = self._queries[-self._max_queries:]
            
            # 记录慢查询
            if query_info['is_slow']:
                logger.warning(f"慢查询检测: {duration:.3f}s - {sql[:100]}...")
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        with self._lock:
            slow_queries = [q for q in self._queries if q['is_slow']]
            return sorted(slow_queries, key=lambda x: x['duration'], reverse=True)[:limit]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        with self._lock:
            if not self._queries:
                return {'total_queries': 0, 'avg_duration': 0, 'slow_queries': 0}
            
            total_queries = len(self._queries)
            avg_duration = sum(q['duration'] for q in self._queries) / total_queries
            slow_queries = sum(1 for q in self._queries if q['is_slow'])
            
            return {
                'total_queries': total_queries,
                'avg_duration': avg_duration,
                'slow_queries': slow_queries,
                'slow_query_rate': slow_queries / total_queries if total_queries > 0 else 0
            }
    
    def clear_queries(self):
        """清空查询记录"""
        with self._lock:
            self._queries.clear()


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self._profiler = QueryProfiler()
        self._index_suggestions: List[Dict[str, Any]] = []
        self._query_patterns: Dict[str, int] = {}
        
    def profile_query(self, sql: str, params: Dict = None):
        """查询性能分析装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self._profiler.record_query(sql, duration, params)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self._profiler.record_query(f"{sql} (ERROR: {e})", duration, params)
                    raise
            return wrapper
        return decorator
    
    def analyze_query_patterns(self):
        """分析查询模式"""
        with self._profiler._lock:
            for query in self._profiler._queries:
                # 提取查询模式（去除参数值）
                pattern = self._extract_query_pattern(query['sql'])
                self._query_patterns[pattern] = self._query_patterns.get(pattern, 0) + 1
    
    def _extract_query_pattern(self, sql: str) -> str:
        """提取查询模式"""
        # 简单的模式提取，去除参数值
        import re
        # 替换数字参数
        pattern = re.sub(r'\b\d+\b', '?', sql)
        # 替换字符串参数
        pattern = re.sub(r"'[^']*'", '?', pattern)
        return pattern.strip()
    
    def suggest_indexes(self) -> List[Dict[str, Any]]:
        """建议索引优化"""
        suggestions = []
        
        # 分析WHERE子句中的列
        with self._profiler._lock:
            for query in self._profiler._queries:
                if query['is_slow'] and 'WHERE' in query['sql'].upper():
                    # 简单的索引建议逻辑
                    suggestion = {
                        'query': query['sql'][:100] + '...',
                        'duration': query['duration'],
                        'suggestion': '考虑在WHERE子句的列上添加索引',
                        'priority': 'high' if query['duration'] > 2.0 else 'medium'
                    }
                    suggestions.append(suggestion)
        
        return suggestions
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        stats = self._profiler.get_query_stats()
        slow_queries = self._profiler.get_slow_queries(5)
        suggestions = self.suggest_indexes()
        
        return {
            'query_stats': stats,
            'slow_queries': slow_queries,
            'index_suggestions': suggestions,
            'optimization_score': self._calculate_optimization_score(stats)
        }
    
    def _calculate_optimization_score(self, stats: Dict[str, Any]) -> int:
        """计算优化分数 (0-100)"""
        if stats['total_queries'] == 0:
            return 100
        
        # 基于平均响应时间和慢查询率计算分数
        avg_score = max(0, 100 - int(stats['avg_duration'] * 50))
        slow_score = max(0, 100 - int(stats['slow_query_rate'] * 100))
        
        return min(avg_score, slow_score)


class DatabaseIndexManager:
    """数据库索引管理器"""
    
    def __init__(self):
        self._indexes: List[Dict[str, Any]] = []
        self._recommended_indexes: List[Dict[str, Any]] = []
    
    def analyze_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """分析表索引"""
        try:
            with db_manager.get_session(get_database_url()) as session:
                # 获取表索引信息
                if 'sqlite' in get_database_url():
                    # SQLite索引查询
                    result = session.execute(text(f"PRAGMA index_list({table_name})"))
                    indexes = []
                    for row in result:
                        indexes.append({
                            'name': row[1],
                            'unique': bool(row[2]),
                            'origin': row[3],
                            'partial': bool(row[4])
                        })
                    return indexes
                else:
                    # 其他数据库的索引查询
                    result = session.execute(text(f"""
                        SELECT index_name, column_name, is_unique
                        FROM information_schema.statistics 
                        WHERE table_name = '{table_name}'
                    """))
                    return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"分析表索引失败: {e}")
            return []
    
    def recommend_indexes(self, table_name: str, columns: List[str]) -> List[Dict[str, Any]]:
        """推荐索引"""
        recommendations = []
        
        for column in columns:
            recommendation = {
                'table': table_name,
                'column': column,
                'index_name': f"idx_{table_name}_{column}",
                'type': 'btree',
                'priority': 'medium',
                'reason': f'在 {table_name}.{column} 上创建索引以提高查询性能'
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def create_index(self, table_name: str, column: str, index_name: str = None) -> bool:
        """创建索引"""
        try:
            if not index_name:
                index_name = f"idx_{table_name}_{column}"
            
            with db_manager.get_session(get_database_url()) as session:
                sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column})"
                session.execute(text(sql))
                session.commit()
                logger.info(f"索引创建成功: {index_name}")
                return True
        except Exception as e:
            logger.error(f"创建索引失败: {e}")
            return False


# 全局查询优化器实例
query_optimizer = QueryOptimizer()
index_manager = DatabaseIndexManager()


def optimize_query(func):
    """查询优化装饰器"""
    return query_optimizer.profile_query("", {})(func)


def get_query_performance_report() -> Dict[str, Any]:
    """获取查询性能报告"""
    return query_optimizer.get_optimization_report()


def analyze_database_performance() -> Dict[str, Any]:
    """分析数据库性能"""
    report = query_optimizer.get_optimization_report()
    
    # 分析主要表的索引
    main_tables = ['users', 'shops', 'messages', 'knowledge_base_items']
    table_analysis = {}
    
    for table in main_tables:
        try:
            indexes = index_manager.analyze_table_indexes(table)
            table_analysis[table] = {
                'indexes': indexes,
                'index_count': len(indexes)
            }
        except Exception as e:
            table_analysis[table] = {'error': str(e)}
    
    report['table_analysis'] = table_analysis
    return report
