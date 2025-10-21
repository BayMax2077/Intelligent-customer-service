# -*- coding: utf-8 -*-
"""
测试配置：测试环境配置和常量

运行：
  .\.venv\Scripts\python -m pytest tests/test_config.py -q
"""

import pytest
import os
import tempfile
from pathlib import Path


class TestConfig:
    """测试配置类"""
    
    # 测试数据库
    TEST_DATABASE_URL = "sqlite:///:memory:"
    
    # 测试用户
    TEST_ADMIN_USERNAME = "admin"
    TEST_ADMIN_PASSWORD = "admin"
    TEST_ADMIN_ROLE = "superadmin"
    
    # 测试店铺
    TEST_SHOP_NAME = "测试店铺"
    TEST_SHOP_QIANNIU_TITLE = "千牛测试"
    
    # 测试知识库
    TEST_KB_QUESTION = "如何退款？"
    TEST_KB_ANSWER = "请提供订单号，我们为您处理退款。"
    TEST_KB_CATEGORY = "售后"
    TEST_KB_KEYWORDS = "退款,退货"
    
    # 测试消息
    TEST_MESSAGE_CONTENT = "我要退款"
    TEST_MESSAGE_CUSTOMER_ID = "test_customer"
    TEST_MESSAGE_SOURCE = "qianniu"
    
    # 测试OCR配置 (x, y, width, height)
    TEST_OCR_REGION = [200, 200, 600, 300]
    TEST_UNREAD_THRESHOLD = 0.02
    
    # 测试AI配置
    TEST_AI_MODEL = "stub"
    TEST_AI_CONFIDENCE = 0.8
    
    # 测试超时设置
    TEST_TIMEOUT = 30  # 秒
    
    # 测试重试次数
    TEST_RETRY_COUNT = 3
    
    # 测试并发数
    TEST_CONCURRENT_COUNT = 5
    
    # 测试数据量
    TEST_BATCH_SIZE = 100
    
    # 测试文件路径
    TEST_REPORTS_DIR = "reports"
    TEST_LOGS_DIR = "logs"
    TEST_DATA_DIR = "data"
    
    # 测试环境变量
    TEST_ENV_VARS = {
        "SECRET_KEY": "test-secret-key",
        "DATABASE_URL": TEST_DATABASE_URL,
        "TESTING": "true",
        "WTF_CSRF_ENABLED": "false",
    }
    
    # 测试API端点
    TEST_API_ENDPOINTS = {
        "health": "/health",
        "login": "/api/auth/login",
        "shops": "/api/shops",
        "messages": "/api/messages",
        "audit": "/api/audit",
        "kb": "/api/kb",
        "statistics": "/api/statistics/daily",
        "users": "/api/users",
    }
    
    # 测试响应状态码
    TEST_STATUS_CODES = {
        "success": 200,
        "created": 201,
        "bad_request": 400,
        "unauthorized": 401,
        "forbidden": 403,
        "not_found": 404,
        "server_error": 500,
    }
    
    # 测试标记
    TEST_MARKERS = {
        "unit": "unit",
        "integration": "integration",
        "frontend": "frontend",
        "backend": "backend",
        "slow": "slow",
        "performance": "performance",
        "smoke": "smoke",
    }


@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    return TestConfig()


def test_config_validation(test_config):
    """测试配置验证"""
    # 验证数据库URL
    assert test_config.TEST_DATABASE_URL.startswith("sqlite://")
    
    # 验证用户配置
    assert test_config.TEST_ADMIN_USERNAME == "admin"
    assert test_config.TEST_ADMIN_PASSWORD == "admin"
    assert test_config.TEST_ADMIN_ROLE == "superadmin"
    
    # 验证店铺配置
    assert test_config.TEST_SHOP_NAME == "测试店铺"
    assert test_config.TEST_SHOP_QIANNIU_TITLE == "千牛测试"
    
    # 验证知识库配置
    assert test_config.TEST_KB_QUESTION == "如何退款？"
    assert test_config.TEST_KB_ANSWER == "请提供订单号，我们为您处理退款。"
    assert test_config.TEST_KB_CATEGORY == "售后"
    assert test_config.TEST_KB_KEYWORDS == "退款,退货"
    
    # 验证消息配置
    assert test_config.TEST_MESSAGE_CONTENT == "我要退款"
    assert test_config.TEST_MESSAGE_CUSTOMER_ID == "test_customer"
    assert test_config.TEST_MESSAGE_SOURCE == "qianniu"
    
    # 验证OCR配置
    assert len(test_config.TEST_OCR_REGION) == 4
    assert all(isinstance(x, int) for x in test_config.TEST_OCR_REGION)
    assert test_config.TEST_UNREAD_THRESHOLD == 0.02
    
    # 验证AI配置
    assert test_config.TEST_AI_MODEL == "stub"
    assert test_config.TEST_AI_CONFIDENCE == 0.8
    
    # 验证超时设置
    assert test_config.TEST_TIMEOUT == 30
    assert test_config.TEST_RETRY_COUNT == 3
    assert test_config.TEST_CONCURRENT_COUNT == 5
    assert test_config.TEST_BATCH_SIZE == 100
    
    # 验证目录配置
    assert test_config.TEST_REPORTS_DIR == "reports"
    assert test_config.TEST_LOGS_DIR == "logs"
    assert test_config.TEST_DATA_DIR == "data"
    
    # 验证环境变量
    assert "SECRET_KEY" in test_config.TEST_ENV_VARS
    assert "DATABASE_URL" in test_config.TEST_ENV_VARS
    assert "TESTING" in test_config.TEST_ENV_VARS
    assert "WTF_CSRF_ENABLED" in test_config.TEST_ENV_VARS
    
    # 验证API端点
    assert "health" in test_config.TEST_API_ENDPOINTS
    assert "login" in test_config.TEST_API_ENDPOINTS
    assert "shops" in test_config.TEST_API_ENDPOINTS
    assert "messages" in test_config.TEST_API_ENDPOINTS
    assert "audit" in test_config.TEST_API_ENDPOINTS
    assert "kb" in test_config.TEST_API_ENDPOINTS
    assert "statistics" in test_config.TEST_API_ENDPOINTS
    assert "users" in test_config.TEST_API_ENDPOINTS
    
    # 验证状态码
    assert test_config.TEST_STATUS_CODES["success"] == 200
    assert test_config.TEST_STATUS_CODES["created"] == 201
    assert test_config.TEST_STATUS_CODES["bad_request"] == 400
    assert test_config.TEST_STATUS_CODES["unauthorized"] == 401
    assert test_config.TEST_STATUS_CODES["forbidden"] == 403
    assert test_config.TEST_STATUS_CODES["not_found"] == 404
    assert test_config.TEST_STATUS_CODES["server_error"] == 500
    
    # 验证标记
    assert "unit" in test_config.TEST_MARKERS
    assert "integration" in test_config.TEST_MARKERS
    assert "frontend" in test_config.TEST_MARKERS
    assert "backend" in test_config.TEST_MARKERS
    assert "slow" in test_config.TEST_MARKERS
    assert "performance" in test_config.TEST_MARKERS
    assert "smoke" in test_config.TEST_MARKERS


def test_environment_setup(test_config):
    """测试环境设置"""
    # 设置测试环境变量
    for key, value in test_config.TEST_ENV_VARS.items():
        os.environ[key] = value
    
    # 验证环境变量设置
    assert os.environ.get("SECRET_KEY") == "test-secret-key"
    assert os.environ.get("DATABASE_URL") == test_config.TEST_DATABASE_URL
    assert os.environ.get("TESTING") == "true"
    assert os.environ.get("WTF_CSRF_ENABLED") == "false"
    
    # 清理环境变量
    for key in test_config.TEST_ENV_VARS.keys():
        if key in os.environ:
            del os.environ[key]


def test_directory_creation(test_config):
    """测试目录创建"""
    # 创建测试目录
    for directory in [test_config.TEST_REPORTS_DIR, test_config.TEST_LOGS_DIR, test_config.TEST_DATA_DIR]:
        Path(directory).mkdir(exist_ok=True)
        assert Path(directory).exists()
        assert Path(directory).is_dir()


def test_file_paths(test_config):
    """测试文件路径"""
    # 验证文件路径格式
    assert test_config.TEST_DATABASE_URL.startswith("sqlite://")
    assert test_config.TEST_REPORTS_DIR == "reports"
    assert test_config.TEST_LOGS_DIR == "logs"
    assert test_config.TEST_DATA_DIR == "data"


def test_api_endpoints_format(test_config):
    """测试API端点格式"""
    for endpoint_name, endpoint_path in test_config.TEST_API_ENDPOINTS.items():
        # 验证端点路径格式
        assert endpoint_path.startswith("/")
        assert endpoint_name in ["health", "login", "shops", "messages", "audit", "kb", "statistics", "users"]


def test_status_codes_range(test_config):
    """测试状态码范围"""
    for status_name, status_code in test_config.TEST_STATUS_CODES.items():
        # 验证状态码范围
        assert 100 <= status_code <= 599
        assert status_name in ["success", "created", "bad_request", "unauthorized", "forbidden", "not_found", "server_error"]


def test_markers_format(test_config):
    """测试标记格式"""
    for marker_name, marker_value in test_config.TEST_MARKERS.items():
        # 验证标记格式
        assert isinstance(marker_name, str)
        assert isinstance(marker_value, str)
        assert marker_name == marker_value
        assert marker_name in ["unit", "integration", "frontend", "backend", "slow", "performance", "smoke"]


def test_config_consistency(test_config):
    """测试配置一致性"""
    # 验证配置项之间的一致性
    assert test_config.TEST_ADMIN_USERNAME == "admin"
    assert test_config.TEST_ADMIN_PASSWORD == "admin"
    assert test_config.TEST_ADMIN_ROLE == "superadmin"
    
    # 验证OCR配置一致性
    assert len(test_config.TEST_OCR_REGION) == 4
    assert test_config.TEST_OCR_REGION[0] >= 0  # x >= 0
    assert test_config.TEST_OCR_REGION[1] >= 0  # y >= 0
    assert test_config.TEST_OCR_REGION[2] > 0   # width > 0
    assert test_config.TEST_OCR_REGION[3] > 0   # height > 0
    
    # 验证AI配置一致性
    assert 0 <= test_config.TEST_AI_CONFIDENCE <= 1
    assert test_config.TEST_AI_MODEL in ["stub", "openai", "qwen", "ernie"]
    
    # 验证超时配置一致性
    assert test_config.TEST_TIMEOUT > 0
    assert test_config.TEST_RETRY_COUNT > 0
    assert test_config.TEST_CONCURRENT_COUNT > 0
    assert test_config.TEST_BATCH_SIZE > 0


def test_config_importability():
    """测试配置可导入性"""
    # 验证配置类可以正常导入
    from tests.test_config import TestConfig
    
    # 验证配置类实例化
    config = TestConfig()
    assert config is not None
    
    # 验证配置属性访问
    assert hasattr(config, 'TEST_DATABASE_URL')
    assert hasattr(config, 'TEST_ADMIN_USERNAME')
    assert hasattr(config, 'TEST_SHOP_NAME')
    assert hasattr(config, 'TEST_KB_QUESTION')
    assert hasattr(config, 'TEST_MESSAGE_CONTENT')
    assert hasattr(config, 'TEST_OCR_REGION')
    assert hasattr(config, 'TEST_AI_MODEL')
    assert hasattr(config, 'TEST_TIMEOUT')
    assert hasattr(config, 'TEST_RETRY_COUNT')
    assert hasattr(config, 'TEST_CONCURRENT_COUNT')
    assert hasattr(config, 'TEST_BATCH_SIZE')
    assert hasattr(config, 'TEST_REPORTS_DIR')
    assert hasattr(config, 'TEST_LOGS_DIR')
    assert hasattr(config, 'TEST_DATA_DIR')
    assert hasattr(config, 'TEST_ENV_VARS')
    assert hasattr(config, 'TEST_API_ENDPOINTS')
    assert hasattr(config, 'TEST_STATUS_CODES')
    assert hasattr(config, 'TEST_MARKERS')
