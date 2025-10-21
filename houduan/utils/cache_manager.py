"""
缓存管理器
提供内存缓存、Redis缓存和缓存策略管理
"""

from __future__ import annotations

import json
import pickle
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from functools import wraps
from flask import current_app
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis不可用，将使用内存缓存")


class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._access_times: Dict[str, float] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return None
            
            cache_item = self._cache[key]
            
            # 检查是否过期
            if self._is_expired(cache_item):
                self._remove(key)
                return None
            
            # 更新访问时间
            self._access_times[key] = time.time()
            
            return cache_item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            # 检查缓存大小限制
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_oldest()
            
            ttl = ttl or self._default_ttl
            expire_time = time.time() + ttl
            
            self._cache[key] = {
                'value': value,
                'expire_time': expire_time,
                'created_at': time.time()
            }
            self._access_times[key] = time.time()
            
            return True
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            if key in self._cache:
                self._remove(key)
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def _is_expired(self, cache_item: Dict[str, Any]) -> bool:
        """检查缓存项是否过期"""
        return time.time() > cache_item['expire_time']
    
    def _remove(self, key: str):
        """移除缓存项"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
    
    def _evict_oldest(self):
        """驱逐最旧的缓存项"""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove(oldest_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            current_time = time.time()
            expired_count = sum(1 for item in self._cache.values() if self._is_expired(item))
            
            return {
                'total_items': len(self._cache),
                'expired_items': expired_count,
                'active_items': len(self._cache) - expired_count,
                'max_size': self._max_size,
                'usage_rate': len(self._cache) / self._max_size if self._max_size > 0 else 0
            }


class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis不可用，请安装redis包")
        
        self._redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False  # 保持二进制数据
        )
        self._default_ttl = 3600
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            data = self._redis.get(key)
            if data is None:
                return None
            
            # 尝试反序列化
            try:
                return pickle.loads(data)
            except:
                # 如果pickle失败，尝试JSON
                try:
                    return json.loads(data.decode('utf-8'))
                except:
                    return data.decode('utf-8')
        except Exception as e:
            logger.error(f"Redis获取缓存失败: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            ttl = ttl or self._default_ttl
            
            # 尝试序列化
            try:
                data = pickle.dumps(value)
            except:
                # 如果pickle失败，尝试JSON
                try:
                    data = json.dumps(value).encode('utf-8')
                except:
                    data = str(value).encode('utf-8')
            
            return self._redis.setex(key, ttl, data)
        except Exception as e:
            logger.error(f"Redis设置缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        try:
            return bool(self._redis.delete(key))
        except Exception as e:
            logger.error(f"Redis删除缓存失败: {e}")
            return False
    
    def clear(self):
        """清空缓存"""
        try:
            self._redis.flushdb()
        except Exception as e:
            logger.error(f"Redis清空缓存失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            info = self._redis.info()
            return {
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_usage': info.get('used_memory_human', '0B'),
                'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1)
            }
        except Exception as e:
            logger.error(f"获取Redis统计信息失败: {e}")
            return {}


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self._caches: Dict[str, Union[MemoryCache, RedisCache]] = {}
        self._default_cache = "memory"
        self._cache_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
    def register_cache(self, name: str, cache: Union[MemoryCache, RedisCache]):
        """注册缓存实例"""
        with self._lock:
            self._caches[name] = cache
            logger.info(f"缓存已注册: {name}")
    
    def get_cache(self, name: str = None) -> Union[MemoryCache, RedisCache]:
        """获取缓存实例"""
        cache_name = name or self._default_cache
        with self._lock:
            return self._caches.get(cache_name)
    
    def create_memory_cache(self, name: str, max_size: int = 1000, default_ttl: int = 3600):
        """创建内存缓存"""
        cache = MemoryCache(max_size, default_ttl)
        self.register_cache(name, cache)
        return cache
    
    def create_redis_cache(self, name: str, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        """创建Redis缓存"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis不可用，创建内存缓存替代")
            return self.create_memory_cache(name)
        
        try:
            cache = RedisCache(host, port, db, password)
            self.register_cache(name, cache)
            return cache
        except Exception as e:
            logger.error(f"创建Redis缓存失败: {e}")
            return self.create_memory_cache(name)
    
    def cache_result(self, key_prefix: str = "", ttl: int = 3600, cache_name: str = None):
        """缓存结果装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # 获取缓存
                cache = self.get_cache(cache_name)
                if cache:
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        logger.debug(f"缓存命中: {cache_key}")
                        return cached_result
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                if cache:
                    cache.set(cache_key, result, ttl)
                    logger.debug(f"结果已缓存: {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    def invalidate_cache(self, pattern: str, cache_name: str = None):
        """使缓存失效"""
        cache = self.get_cache(cache_name)
        if not cache:
            return False
        
        # 简单的模式匹配（实际项目中可能需要更复杂的模式匹配）
        if hasattr(cache, '_cache'):  # MemoryCache
            with cache._lock:
                keys_to_remove = [key for key in cache._cache.keys() if pattern in key]
                for key in keys_to_remove:
                    cache.delete(key)
                return len(keys_to_remove) > 0
        else:  # RedisCache
            # Redis需要扫描键，这里简化处理
            return True
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取所有缓存统计信息"""
        with self._lock:
            stats = {}
            for name, cache in self._caches.items():
                try:
                    stats[name] = cache.get_stats()
                except Exception as e:
                    stats[name] = {'error': str(e)}
            return stats
    
    def optimize_caches(self) -> Dict[str, Any]:
        """优化缓存配置"""
        optimization_results = {}
        
        for name, cache in self._caches.items():
            try:
                stats = cache.get_stats()
                suggestions = []
                
                # 内存缓存优化建议
                if isinstance(cache, MemoryCache):
                    usage_rate = stats.get('usage_rate', 0)
                    if usage_rate > 0.8:
                        suggestions.append({
                            'type': 'increase_size',
                            'message': '缓存使用率过高，建议增加缓存大小',
                            'priority': 'high'
                        })
                    elif usage_rate < 0.2:
                        suggestions.append({
                            'type': 'decrease_size',
                            'message': '缓存使用率过低，建议减少缓存大小',
                            'priority': 'medium'
                        })
                
                optimization_results[name] = {
                    'stats': stats,
                    'suggestions': suggestions,
                    'optimization_score': self._calculate_cache_score(stats)
                }
                
            except Exception as e:
                optimization_results[name] = {'error': str(e)}
        
        return optimization_results
    
    def _calculate_cache_score(self, stats: Dict[str, Any]) -> int:
        """计算缓存优化分数"""
        if not stats:
            return 0
        
        score = 100
        
        # 基于使用率调整分数
        usage_rate = stats.get('usage_rate', 0)
        if usage_rate > 0.9:
            score -= 30
        elif usage_rate < 0.1:
            score -= 20
        
        # 基于命中率调整分数（如果有的话）
        hit_rate = stats.get('hit_rate', 0)
        if hit_rate < 0.5:
            score -= 20
        
        return max(0, min(100, score))


# 全局缓存管理器
cache_manager = CacheManager()

# 初始化默认缓存
cache_manager.create_memory_cache("memory", max_size=1000, default_ttl=3600)

# 尝试创建Redis缓存
try:
    cache_manager.create_redis_cache("redis", host="localhost", port=6379)
except Exception as e:
    logger.warning(f"Redis缓存初始化失败: {e}")


def cached(key_prefix: str = "", ttl: int = 3600, cache_name: str = None):
    """缓存装饰器"""
    return cache_manager.cache_result(key_prefix, ttl, cache_name)


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    return cache_manager.get_cache_stats()


def optimize_caches() -> Dict[str, Any]:
    """优化缓存配置"""
    return cache_manager.optimize_caches()
