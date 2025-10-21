# -*- coding: utf-8 -*-
"""
测试配置文件：pytest 配置和共享 fixtures

运行：
  .\.venv\Scripts\python -m pytest -q
"""

import pytest
import os
import tempfile
import json
from datetime import datetime, timedelta

from houduan.app import create_app, db
from houduan.models import User, Shop, Message, KnowledgeBaseItem, AIReply, AuditQueueItem
from houduan.utils.security import hash_password


@pytest.fixture(scope="session")
def test_app():
    """创建测试应用实例"""
    # 使用临时 SQLite 数据库
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    
    with app.app_context():
        db.create_all()
        # 创建默认管理员
        admin = User(
            username="admin", 
            password_hash=hash_password("admin"), 
            role="superadmin"
        )
        db.session.add(admin)
        db.session.commit()
    
    yield app
    
    # 清理
    with app.app_context():
        db.session.remove()
        try:
            db.engine.dispose()
        except Exception:
            pass
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def client(test_app):
    """创建测试客户端"""
    with test_app.test_client() as client:
        yield client


@pytest.fixture()
def auth_headers(client):
    """获取认证头"""
    # 登录获取token
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin"
    })
    assert resp.status_code == 200
    
    # 这里简化处理，实际应该从响应中提取token
    return {"Authorization": "Bearer admin_token"}


@pytest.fixture()
def test_shop(test_app):
    """创建测试店铺"""
    with test_app.app_context():
        shop = Shop(
            name="测试店铺",
            qianniu_title="千牛测试",
            config_json=json.dumps({
                "ocr_region": [800, 200, 600, 300],
                "unread_threshold": 0.02,
                "ai_model": "stub",
                "auto_mode": True
            })
        )
        db.session.add(shop)
        db.session.commit()
        yield shop


@pytest.fixture()
def test_messages(test_app, test_shop):
    """创建测试消息"""
    with test_app.app_context():
        messages = []
        for i in range(5):
            message = Message(
                shop_id=test_shop.id,
                customer_id=f"customer_{i}",
                content=f"测试消息{i}",
                source="qianniu",
                status="new"
            )
            db.session.add(message)
            messages.append(message)
        db.session.commit()
        yield messages


@pytest.fixture()
def test_knowledge_base(test_app):
    """创建测试知识库"""
    with test_app.app_context():
        kb_items = []
        test_data = [
            {
                "question": "如何退款？",
                "answer": "请提供订单号，我们为您处理退款。",
                "category": "售后",
                "keywords": "退款,退货"
            },
            {
                "question": "如何发货？",
                "answer": "我们会在24小时内发货。",
                "category": "发货",
                "keywords": "发货,物流"
            },
            {
                "question": "如何联系客服？",
                "answer": "请拨打客服电话400-xxx-xxxx。",
                "category": "联系",
                "keywords": "客服,电话"
            }
        ]
        
        for data in test_data:
            item = KnowledgeBaseItem(**data)
            db.session.add(item)
            kb_items.append(item)
        
        db.session.commit()
        yield kb_items


@pytest.fixture()
def test_audit_items(test_app, test_messages):
    """创建测试审核项"""
    with test_app.app_context():
        audit_items = []
        for message in test_messages:
            # 创建AI回复
            ai_reply = AIReply(
                message_id=message.id,
                model="stub",
                reply=f"AI回复：{message.content}",
                confidence=0.8,
                review_status="pending"
            )
            db.session.add(ai_reply)
            
            # 创建审核项
            audit_item = AuditQueueItem(
                message_id=message.id,
                status="pending"
            )
            db.session.add(audit_item)
            audit_items.append(audit_item)
        
        db.session.commit()
        yield audit_items


@pytest.fixture()
def test_users(test_app):
    """创建测试用户"""
    with test_app.app_context():
        users = []
        test_user_data = [
            {"username": "agent1", "role": "agent", "shop_id": 1},
            {"username": "agent2", "role": "agent", "shop_id": 1},
            {"username": "admin1", "role": "admin", "shop_id": None},
        ]
        
        for data in test_user_data:
            user = User(
                username=data["username"],
                password_hash=hash_password("test_password"),
                role=data["role"],
                shop_id=data["shop_id"]
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        yield users


@pytest.fixture()
def test_statistics_data(test_app, test_shop):
    """创建测试统计数据"""
    with test_app.app_context():
        # 创建历史消息数据
        for i in range(30):
            message = Message(
                shop_id=test_shop.id,
                customer_id=f"customer_{i}",
                content=f"历史消息{i}",
                source="qianniu",
                status="answered",
                created_at=datetime.now() - timedelta(days=i)
            )
            db.session.add(message)
        
        db.session.commit()
        yield


@pytest.fixture(autouse=True)
def clean_database(test_app):
    """每个测试后清理数据库"""
    yield
    with test_app.app_context():
        # 清理所有表
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # 重新创建默认管理员
        admin = User(
            username="admin", 
            password_hash=hash_password("admin"), 
            role="superadmin"
        )
        db.session.add(admin)
        db.session.commit()


@pytest.fixture()
def mock_ai_response():
    """模拟AI响应"""
    return {
        "reply": "这是AI生成的回复",
        "confidence": 0.85,
        "model": "stub"
    }


@pytest.fixture()
def mock_ocr_response():
    """模拟OCR响应"""
    return {
        "text": "这是OCR识别的文本",
        "confidence": 0.9,
        "region": [800, 200, 600, 300]
    }


@pytest.fixture()
def mock_qianniu_windows():
    """模拟千牛窗口列表"""
    return [
        {"title": "千牛-测试店铺1", "hwnd": 12345},
        {"title": "千牛-测试店铺2", "hwnd": 12346},
    ]


@pytest.fixture()
def test_config():
    """测试配置"""
    return {
        "SECRET_KEY": "test-secret-key",
        "DATABASE_URL": "sqlite:///:memory:",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    }


@pytest.fixture()
def test_environment_variables():
    """测试环境变量"""
    env_vars = {
        "SECRET_KEY": "test-secret-key",
        "DATABASE_URL": "sqlite:///:memory:",
        "OPENAI_API_KEY": "test-openai-key",
        "QWEN_API_KEY": "test-qwen-key",
        "ERNIE_API_KEY": "test-ernie-key",
        "ERNIE_SECRET_KEY": "test-ernie-secret",
    }
    
    # 设置环境变量
    for key, value in env_vars.items():
        os.environ[key] = value
    
    yield env_vars
    
    # 清理环境变量
    for key in env_vars.keys():
        if key in os.environ:
            del os.environ[key]


# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "frontend: marks tests as frontend tests"
    )
    config.addinivalue_line(
        "markers", "backend: marks tests as backend tests"
    )


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 根据文件路径自动标记测试
        if "test_frontend" in item.fspath.strpath:
            item.add_marker(pytest.mark.frontend)
        elif "test_integration" in item.fspath.strpath:
            item.add_marker(pytest.mark.integration)
        elif "test_api" in item.fspath.strpath:
            item.add_marker(pytest.mark.backend)
        
        # 根据测试名称标记慢测试
        if "performance" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)


# 测试报告钩子（需要pytest-html插件）
# def pytest_html_report_title(report):
#     """设置HTML报告标题"""
#     report.title = "智能客服系统测试报告"


# 测试失败时的额外信息
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    if call.when == "call":
        # 在测试失败时添加额外信息
        if call.excinfo is not None:
            # 可以在这里添加失败时的截图、日志等
            pass


# 测试会话开始和结束
def pytest_sessionstart(session):
    """测试会话开始"""
    print("\n开始智能客服系统测试...")
    print("=" * 50)


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束"""
    print("\n" + "=" * 50)
    if exitstatus == 0:
        print("所有测试通过！")
    else:
        print(f"测试失败，退出状态: {exitstatus}")
    print("测试会话结束")


# 测试失败时的清理
def pytest_runtest_teardown(item, nextitem):
    """测试清理"""
    # 可以在这里添加测试失败时的清理逻辑
    pass
