"""
API适配器模式
支持在简化版和完整版API之间动态切换
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify
from loguru import logger

from . import api_bp
from ..utils.db_manager import db_manager, get_database_url


class APIAdapter:
    """API适配器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self._fallback_mode = False
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        raise NotImplementedError
    
    def handle_request(self, *args, **kwargs):
        """处理请求"""
        raise NotImplementedError
    
    def get_fallback_response(self, error: str = "API不可用") -> Dict[str, Any]:
        """获取回退响应"""
        return {
            "error": "api_unavailable",
            "message": error,
            "fallback_mode": True
        }


class DatabaseAPIAdapter(APIAdapter):
    """数据库API适配器"""
    
    def __init__(self):
        super().__init__("database")
        self._db_available = None
        self._last_check = None
    
    def is_available(self) -> bool:
        """检查数据库是否可用"""
        try:
            # 检查数据库健康状态
            health_info = db_manager.health_check(get_database_url())
            self._db_available = health_info['status'] == 'healthy'
            return self._db_available
        except Exception as e:
            logger.warning(f"数据库可用性检查失败: {e}")
            self._db_available = False
            return False
    
    def handle_request(self, operation, *args, **kwargs):
        """处理数据库请求"""
        if not self.is_available():
            return self.get_fallback_response("数据库连接不可用")
        
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            return self.get_fallback_response(f"数据库操作失败: {str(e)}")


class APIAdapterManager:
    """API适配器管理器"""
    
    def __init__(self):
        self._adapters: Dict[str, APIAdapter] = {}
        self._default_mode = "simple"  # 默认使用简化版
        self._force_mode: Optional[str] = None
    
    def register_adapter(self, name: str, adapter: APIAdapter):
        """注册适配器"""
        self._adapters[name] = adapter
        logger.info(f"注册API适配器: {name}")
    
    def set_force_mode(self, mode: Optional[str]):
        """设置强制模式"""
        self._force_mode = mode
        logger.info(f"设置强制API模式: {mode}")
    
    def get_available_mode(self) -> str:
        """获取可用的API模式"""
        if self._force_mode:
            return self._force_mode
        
        # 检查数据库是否可用
        db_adapter = self._adapters.get("database")
        if db_adapter and db_adapter.is_available():
            return "full"
        else:
            return "simple"
    
    def should_use_simple_api(self) -> bool:
        """是否应该使用简化版API"""
        return self.get_available_mode() == "simple"
    
    def get_adapter(self, name: str) -> Optional[APIAdapter]:
        """获取适配器"""
        return self._adapters.get(name)


# 全局API适配器管理器
api_adapter_manager = APIAdapterManager()

# 注册数据库适配器
api_adapter_manager.register_adapter("database", DatabaseAPIAdapter())


def get_api_mode() -> str:
    """获取当前API模式"""
    return api_adapter_manager.get_available_mode()


def should_use_simple_api() -> bool:
    """是否应该使用简化版API"""
    return api_adapter_manager.should_use_simple_api()


def set_api_mode(mode: str):
    """设置API模式"""
    if mode in ["simple", "full"]:
        api_adapter_manager.set_force_mode(mode)
    else:
        raise ValueError(f"无效的API模式: {mode}")


def get_api_status() -> Dict[str, Any]:
    """获取API状态"""
    return {
        "current_mode": get_api_mode(),
        "force_mode": api_adapter_manager._force_mode,
        "database_available": api_adapter_manager.get_adapter("database").is_available() if api_adapter_manager.get_adapter("database") else False,
        "adapters": list(api_adapter_manager._adapters.keys())
    }


# API状态端点
@api_bp.get("/api/status")
def api_status():
    """获取API状态"""
    return jsonify(get_api_status())


# API模式切换端点
@api_bp.post("/api/mode")
def set_api_mode_endpoint():
    """设置API模式"""
    data = request.get_json(force=True) or {}
    mode = data.get("mode")
    
    if not mode:
        return jsonify({"error": "mode_required"}), 400
    
    if mode not in ["simple", "full"]:
        return jsonify({"error": "invalid_mode"}), 400
    
    try:
        set_api_mode(mode)
        return jsonify({
            "message": f"API模式已切换到: {mode}",
            "current_mode": get_api_mode()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
