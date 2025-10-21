# -*- coding: utf-8 -*-
"""
测试工具：测试辅助函数和工具类

运行：
  .\.venv\Scripts\python -m pytest tests/test_utils.py -q
"""

import pytest
import json
import time
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_username(prefix: str = "test_user") -> str:
        """生成测试用户名"""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{suffix}"
    
    @staticmethod
    def generate_password(length: int = 8) -> str:
        """生成测试密码"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_email(prefix: str = "test") -> str:
        """生成测试邮箱"""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{suffix}@example.com"
    
    @staticmethod
    def generate_shop_name(prefix: str = "测试店铺") -> str:
        """生成测试店铺名"""
        suffix = random.randint(1, 9999)
        return f"{prefix}{suffix}"
    
    @staticmethod
    def generate_qianniu_title(prefix: str = "千牛测试") -> str:
        """生成测试千牛标题"""
        suffix = random.randint(1, 9999)
        return f"{prefix}{suffix}"
    
    @staticmethod
    def generate_message_content() -> str:
        """生成测试消息内容"""
        messages = [
            "我要退款",
            "如何发货？",
            "联系客服",
            "修改订单",
            "查看物流",
            "发票问题",
            "售后咨询",
            "产品咨询"
        ]
        return random.choice(messages)
    
    @staticmethod
    def generate_customer_id(prefix: str = "customer") -> str:
        """生成测试客户ID"""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}_{suffix}"
    
    @staticmethod
    def generate_kb_question() -> str:
        """生成测试知识库问题"""
        questions = [
            "如何退款？",
            "如何发货？",
            "如何联系客服？",
            "如何修改订单？",
            "如何查看物流？",
            "如何开发票？",
            "如何申请售后？",
            "如何咨询产品？"
        ]
        return random.choice(questions)
    
    @staticmethod
    def generate_kb_answer() -> str:
        """生成测试知识库答案"""
        answers = [
            "请提供订单号，我们为您处理退款。",
            "我们会在24小时内发货。",
            "请拨打客服电话400-xxx-xxxx。",
            "订单发货前可以修改，请联系客服。",
            "可以在订单详情中查看物流信息。",
            "电子发票可在订单详情下载。",
            "请提供订单号和问题描述，我们为您处理。",
            "请提供产品型号，我们为您详细介绍。"
        ]
        return random.choice(answers)
    
    @staticmethod
    def generate_kb_category() -> str:
        """生成测试知识库分类"""
        categories = ["售后", "发货", "联系", "订单", "物流", "发票", "产品"]
        return random.choice(categories)
    
    @staticmethod
    def generate_kb_keywords() -> str:
        """生成测试知识库关键词"""
        keyword_sets = [
            "退款,退货",
            "发货,物流",
            "客服,电话",
            "修改,订单",
            "物流,查询",
            "发票,下载",
            "售后,处理",
            "产品,咨询"
        ]
        return random.choice(keyword_sets)
    
    @staticmethod
    def generate_ocr_region() -> List[int]:
        """生成测试OCR区域"""
        x = random.randint(100, 1000)
        y = random.randint(100, 800)
        width = random.randint(200, 800)
        height = random.randint(100, 600)
        return [x, y, width, height]
    
    @staticmethod
    def generate_unread_threshold() -> float:
        """生成测试未读阈值"""
        return round(random.uniform(0.01, 0.1), 3)
    
    @staticmethod
    def generate_ai_model() -> str:
        """生成测试AI模型"""
        models = ["stub", "openai", "qwen", "ernie"]
        return random.choice(models)
    
    @staticmethod
    def generate_confidence() -> float:
        """生成测试置信度"""
        return round(random.uniform(0.5, 1.0), 2)
    
    @staticmethod
    def generate_business_hours() -> Dict[str, str]:
        """生成测试营业时间"""
        start_hour = random.randint(8, 10)
        end_hour = random.randint(18, 22)
        return {
            "start": f"{start_hour:02d}:00",
            "end": f"{end_hour:02d}:00"
        }
    
    @staticmethod
    def generate_reply_delay() -> int:
        """生成测试回复延迟"""
        return random.randint(1, 5)
    
    @staticmethod
    def generate_blacklist() -> List[str]:
        """生成测试黑名单"""
        count = random.randint(0, 5)
        return [TestDataGenerator.generate_customer_id() for _ in range(count)]
    
    @staticmethod
    def generate_whitelist() -> List[str]:
        """生成测试白名单"""
        count = random.randint(0, 10)
        return [TestDataGenerator.generate_customer_id() for _ in range(count)]


class TestAssertions:
    """测试断言工具类"""
    
    @staticmethod
    def assert_response_success(response, status_code: int = 200):
        """断言响应成功"""
        assert response.status_code == status_code
        assert response.content_type == "application/json"
    
    @staticmethod
    def assert_response_error(response, status_code: int):
        """断言响应错误"""
        assert response.status_code == status_code
    
    @staticmethod
    def assert_json_structure(data: Dict[str, Any], required_keys: List[str]):
        """断言JSON结构"""
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
    
    @staticmethod
    def assert_user_data(user_data: Dict[str, Any]):
        """断言用户数据结构"""
        required_keys = ["id", "username", "role", "is_active"]
        TestAssertions.assert_json_structure(user_data, required_keys)
        assert isinstance(user_data["id"], int)
        assert isinstance(user_data["username"], str)
        assert user_data["role"] in ["user", "agent", "admin", "superadmin"]
        assert isinstance(user_data["is_active"], bool)
    
    @staticmethod
    def assert_shop_data(shop_data: Dict[str, Any]):
        """断言店铺数据结构"""
        required_keys = ["id", "name", "qianniu_title"]
        TestAssertions.assert_json_structure(shop_data, required_keys)
        assert isinstance(shop_data["id"], int)
        assert isinstance(shop_data["name"], str)
        assert isinstance(shop_data["qianniu_title"], str)
    
    @staticmethod
    def assert_message_data(message_data: Dict[str, Any]):
        """断言消息数据结构"""
        required_keys = ["id", "shop_id", "customer_id", "content", "source", "status"]
        TestAssertions.assert_json_structure(message_data, required_keys)
        assert isinstance(message_data["id"], int)
        assert isinstance(message_data["shop_id"], int)
        assert isinstance(message_data["customer_id"], str)
        assert isinstance(message_data["content"], str)
        assert message_data["source"] in ["qianniu", "manual", "api"]
        assert message_data["status"] in ["new", "answered", "review", "queued"]
    
    @staticmethod
    def assert_kb_data(kb_data: Dict[str, Any]):
        """断言知识库数据结构"""
        required_keys = ["id", "question", "answer", "category", "keywords"]
        TestAssertions.assert_json_structure(kb_data, required_keys)
        assert isinstance(kb_data["id"], int)
        assert isinstance(kb_data["question"], str)
        assert isinstance(kb_data["answer"], str)
        assert isinstance(kb_data["category"], str)
        assert isinstance(kb_data["keywords"], str)
    
    @staticmethod
    def assert_audit_data(audit_data: Dict[str, Any]):
        """断言审核数据结构"""
        required_keys = ["id", "message_id", "status"]
        TestAssertions.assert_json_structure(audit_data, required_keys)
        assert isinstance(audit_data["id"], int)
        assert isinstance(audit_data["message_id"], int)
        assert audit_data["status"] in ["pending", "approved", "rejected"]
    
    @staticmethod
    def assert_statistics_data(stats_data: Dict[str, Any]):
        """断言统计数据结构"""
        required_keys = ["daily_data", "summary"]
        TestAssertions.assert_json_structure(stats_data, required_keys)
        assert isinstance(stats_data["daily_data"], list)
        assert isinstance(stats_data["summary"], dict)


class TestHelpers:
    """测试辅助工具类"""
    
    @staticmethod
    def wait_for_condition(condition_func, timeout: int = 10, interval: float = 0.1):
        """等待条件满足"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False
    
    @staticmethod
    def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
        """重试失败的操作"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
    
    @staticmethod
    def generate_test_data(count: int, data_type: str) -> List[Dict[str, Any]]:
        """生成测试数据列表"""
        data_list = []
        for _ in range(count):
            if data_type == "user":
                data_list.append({
                    "username": TestDataGenerator.generate_username(),
                    "password": TestDataGenerator.generate_password(),
                    "email": TestDataGenerator.generate_email(),
                    "role": random.choice(["user", "agent", "admin", "superadmin"])
                })
            elif data_type == "shop":
                data_list.append({
                    "name": TestDataGenerator.generate_shop_name(),
                    "qianniu_title": TestDataGenerator.generate_qianniu_title()
                })
            elif data_type == "message":
                data_list.append({
                    "customer_id": TestDataGenerator.generate_customer_id(),
                    "content": TestDataGenerator.generate_message_content(),
                    "source": "qianniu",
                    "status": random.choice(["new", "answered", "review", "queued"])
                })
            elif data_type == "kb":
                data_list.append({
                    "question": TestDataGenerator.generate_kb_question(),
                    "answer": TestDataGenerator.generate_kb_answer(),
                    "category": TestDataGenerator.generate_kb_category(),
                    "keywords": TestDataGenerator.generate_kb_keywords()
                })
        return data_list
    
    @staticmethod
    def validate_json_response(response, expected_keys: List[str] = None):
        """验证JSON响应"""
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        data = response.get_json()
        assert isinstance(data, (dict, list))
        
        if expected_keys and isinstance(data, dict):
            for key in expected_keys:
                assert key in data, f"Missing expected key: {key}"
        
        return data
    
    @staticmethod
    def compare_objects(obj1: Dict[str, Any], obj2: Dict[str, Any], ignore_keys: List[str] = None):
        """比较两个对象"""
        if ignore_keys is None:
            ignore_keys = []
        
        for key in obj1:
            if key not in ignore_keys:
                assert key in obj2, f"Missing key in obj2: {key}"
                assert obj1[key] == obj2[key], f"Value mismatch for key {key}: {obj1[key]} != {obj2[key]}"
    
    @staticmethod
    def measure_execution_time(func):
        """测量执行时间"""
        start_time = time.time()
        result = func()
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def create_test_file(filename: str, content: str) -> str:
        """创建测试文件"""
        filepath = f"tests/temp_{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    @staticmethod
    def cleanup_test_file(filepath: str):
        """清理测试文件"""
        import os
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass


def test_data_generator():
    """测试数据生成器测试"""
    generator = TestDataGenerator()
    
    # 测试用户名生成
    username = generator.generate_username()
    assert isinstance(username, str)
    assert username.startswith("test_user")
    
    # 测试密码生成
    password = generator.generate_password()
    assert isinstance(password, str)
    assert len(password) == 8
    
    # 测试邮箱生成
    email = generator.generate_email()
    assert isinstance(email, str)
    assert "@example.com" in email
    
    # 测试店铺名生成
    shop_name = generator.generate_shop_name()
    assert isinstance(shop_name, str)
    assert shop_name.startswith("测试店铺")
    
    # 测试千牛标题生成
    qianniu_title = generator.generate_qianniu_title()
    assert isinstance(qianniu_title, str)
    assert qianniu_title.startswith("千牛测试")
    
    # 测试消息内容生成
    message_content = generator.generate_message_content()
    assert isinstance(message_content, str)
    assert len(message_content) > 0
    
    # 测试客户ID生成
    customer_id = generator.generate_customer_id()
    assert isinstance(customer_id, str)
    assert customer_id.startswith("customer")
    
    # 测试知识库问题生成
    kb_question = generator.generate_kb_question()
    assert isinstance(kb_question, str)
    assert len(kb_question) > 0
    
    # 测试知识库答案生成
    kb_answer = generator.generate_kb_answer()
    assert isinstance(kb_answer, str)
    assert len(kb_answer) > 0
    
    # 测试知识库分类生成
    kb_category = generator.generate_kb_category()
    assert isinstance(kb_category, str)
    assert kb_category in ["售后", "发货", "联系", "订单", "物流", "发票", "产品"]
    
    # 测试知识库关键词生成
    kb_keywords = generator.generate_kb_keywords()
    assert isinstance(kb_keywords, str)
    assert "," in kb_keywords
    
    # 测试OCR区域生成
    ocr_region = generator.generate_ocr_region()
    assert isinstance(ocr_region, list)
    assert len(ocr_region) == 4
    assert all(isinstance(x, int) for x in ocr_region)
    
    # 测试未读阈值生成
    unread_threshold = generator.generate_unread_threshold()
    assert isinstance(unread_threshold, float)
    assert 0.01 <= unread_threshold <= 0.1
    
    # 测试AI模型生成
    ai_model = generator.generate_ai_model()
    assert isinstance(ai_model, str)
    assert ai_model in ["stub", "openai", "qwen", "ernie"]
    
    # 测试置信度生成
    confidence = generator.generate_confidence()
    assert isinstance(confidence, float)
    assert 0.5 <= confidence <= 1.0
    
    # 测试营业时间生成
    business_hours = generator.generate_business_hours()
    assert isinstance(business_hours, dict)
    assert "start" in business_hours
    assert "end" in business_hours
    assert business_hours["start"].endswith(":00")
    assert business_hours["end"].endswith(":00")
    
    # 测试回复延迟生成
    reply_delay = generator.generate_reply_delay()
    assert isinstance(reply_delay, int)
    assert 1 <= reply_delay <= 5
    
    # 测试黑名单生成
    blacklist = generator.generate_blacklist()
    assert isinstance(blacklist, list)
    assert len(blacklist) <= 5
    
    # 测试白名单生成
    whitelist = generator.generate_whitelist()
    assert isinstance(whitelist, list)
    assert len(whitelist) <= 10


def test_assertions():
    """测试断言工具测试"""
    assertions = TestAssertions()
    
    # 测试用户数据结构断言
    user_data = {
        "id": 1,
        "username": "test_user",
        "role": "admin",
        "is_active": True
    }
    assertions.assert_user_data(user_data)
    
    # 测试店铺数据结构断言
    shop_data = {
        "id": 1,
        "name": "测试店铺",
        "qianniu_title": "千牛测试"
    }
    assertions.assert_shop_data(shop_data)
    
    # 测试消息数据结构断言
    message_data = {
        "id": 1,
        "shop_id": 1,
        "customer_id": "customer_1",
        "content": "测试消息",
        "source": "qianniu",
        "status": "new"
    }
    assertions.assert_message_data(message_data)
    
    # 测试知识库数据结构断言
    kb_data = {
        "id": 1,
        "question": "如何退款？",
        "answer": "请提供订单号",
        "category": "售后",
        "keywords": "退款,退货"
    }
    assertions.assert_kb_data(kb_data)
    
    # 测试审核数据结构断言
    audit_data = {
        "id": 1,
        "message_id": 1,
        "status": "pending"
    }
    assertions.assert_audit_data(audit_data)
    
    # 测试统计数据结构断言
    stats_data = {
        "daily_data": [],
        "summary": {}
    }
    assertions.assert_statistics_data(stats_data)


def test_helpers():
    """测试辅助工具测试"""
    helpers = TestHelpers()
    
    # 测试等待条件
    def condition():
        return True
    
    result = helpers.wait_for_condition(condition, timeout=1)
    assert result is True
    
    # 测试重试机制
    def failing_func():
        raise Exception("Test exception")
    
    with pytest.raises(Exception):
        helpers.retry_on_failure(failing_func, max_retries=2)
    
    # 测试生成测试数据
    user_data_list = helpers.generate_test_data(5, "user")
    assert len(user_data_list) == 5
    assert all("username" in data for data in user_data_list)
    
    shop_data_list = helpers.generate_test_data(3, "shop")
    assert len(shop_data_list) == 3
    assert all("name" in data for data in shop_data_list)
    
    # 测试测量执行时间
    def test_func():
        time.sleep(0.1)
        return "test_result"
    
    result, execution_time = helpers.measure_execution_time(test_func)
    assert result == "test_result"
    assert execution_time >= 0.1
    
    # 测试创建和清理测试文件
    filepath = helpers.create_test_file("test.txt", "test content")
    assert filepath.startswith("tests/temp_")
    
    helpers.cleanup_test_file(filepath)
    # 文件应该被删除，这里不验证文件是否存在


def test_utility_integration():
    """测试工具集成测试"""
    # 测试数据生成器 + 断言工具
    generator = TestDataGenerator()
    assertions = TestAssertions()
    
    # 生成用户数据并验证
    user_data = {
        "id": 1,
        "username": generator.generate_username(),
        "role": "admin",
        "is_active": True
    }
    assertions.assert_user_data(user_data)
    
    # 生成店铺数据并验证
    shop_data = {
        "id": 1,
        "name": generator.generate_shop_name(),
        "qianniu_title": generator.generate_qianniu_title()
    }
    assertions.assert_shop_data(shop_data)
    
    # 测试辅助工具 + 数据生成器
    helpers = TestHelpers()
    
    # 生成大量测试数据
    user_data_list = helpers.generate_test_data(10, "user")
    assert len(user_data_list) == 10
    
    # 验证所有数据都有必要字段
    for user_data in user_data_list:
        assert "username" in user_data
        assert "password" in user_data
        assert "email" in user_data
        assert "role" in user_data
        assert user_data["role"] in ["user", "agent", "admin", "superadmin"]
