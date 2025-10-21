# -*- coding: utf-8 -*-
"""
后端API测试：认证、店铺、知识库、审核等核心功能

运行：
  .\.venv\Scripts\python -m pytest -q
"""

import json
import os
import tempfile
import pytest
from datetime import datetime, timedelta

from houduan.app import create_app, db
from houduan.models import User, Shop, Message, KnowledgeBaseItem, AIReply, AuditQueueItem
from houduan.utils.security import hash_password


@pytest.fixture()
def app_client():
    # 使用临时 SQLite 数据库，隔离测试
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    with app.app_context():
        db.create_all()
        # 创建默认管理员
        admin = User(username="admin", password_hash=hash_password("admin"), role="superadmin")
        db.session.add(admin)
        db.session.commit()

    try:
        with app.test_client() as client:
            yield client
    finally:
        # 确保完全释放 SQLite 句柄后再删除文件（Windows 下需要显式 dispose）
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


def test_login_success(app_client):
    resp = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["user"]["role"] == "superadmin"


def test_shops_crud_flow(app_client):
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200

    # 创建店铺
    resp = app_client.post("/api/shops", json={"name": "旗舰店", "qianniu_title": "千牛-旗舰店"})
    assert resp.status_code == 200
    shop_id = resp.get_json()["id"]

    # 列表
    resp = app_client.get("/api/shops")
    assert resp.status_code == 200
    items = resp.get_json()
    assert any(it["id"] == shop_id for it in items)

    # 更新
    resp = app_client.put(f"/api/shops/{shop_id}", json={"name": "旗舰店-更新"})
    assert resp.status_code == 200

    # 删除（需要 superadmin，已具备）
    resp = app_client.delete(f"/api/shops/{shop_id}")
    assert resp.status_code == 200

    # 再次列表，确认删除
    resp = app_client.get("/api/shops")
    ids = [it["id"] for it in resp.get_json()]
    assert shop_id not in ids


def test_health_check(app_client):
    """测试健康检查接口"""
    resp = app_client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data


def test_shop_config(app_client):
    """测试店铺配置"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建店铺
    resp = app_client.post("/api/shops", json={"name": "测试店铺", "qianniu_title": "千牛测试"})
    assert resp.status_code == 200
    shop_id = resp.get_json()["id"]
    
    # 设置配置
    config_data = {
        "ocr_region": [800, 200, 600, 300],
        "unread_threshold": 0.02,
        "ai_model": "stub",
        "auto_mode": True,
        "blacklist": ["spam_user"],
        "whitelist": ["vip_user"],
        "business_hours": {"start": "09:00", "end": "22:00"},
        "reply_delay": 3
    }
    
    resp = app_client.put(f"/api/shops/{shop_id}/config", json=config_data)
    assert resp.status_code == 200
    
    # 获取配置
    resp = app_client.get(f"/api/shops/{shop_id}/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ocr_region"] == [800, 200, 600, 300]
    assert data["unread_threshold"] == 0.02
    assert data["ai_model"] == "stub"
    assert data["auto_mode"] is True


def test_knowledge_base_crud(app_client):
    """测试知识库CRUD操作"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建知识库条目
    kb_data = {
        "question": "如何退款？",
        "answer": "请提供订单号，我们为您处理退款。",
        "category": "售后",
        "keywords": "退款,退货"
    }
    
    resp = app_client.post("/api/kb", json=kb_data)
    assert resp.status_code == 201
    data = resp.get_json()
    kb_id = data["id"]
    
    # 获取知识库条目
    resp = app_client.get(f"/api/kb/{kb_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["question"] == "如何退款？"
    
    # 更新知识库条目
    update_data = {
        "answer": "请提供订单号和退款原因，我们为您处理退款。"
    }
    resp = app_client.put(f"/api/kb/{kb_id}", json=update_data)
    assert resp.status_code == 200
    
    # 删除知识库条目
    resp = app_client.delete(f"/api/kb/{kb_id}")
    assert resp.status_code == 200


def test_knowledge_base_search(app_client):
    """测试知识库搜索"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建测试知识库条目
    kb_item = KnowledgeBaseItem(
        question="如何退款？",
        answer="请提供订单号，我们为您处理退款。",
        category="售后",
        keywords="退款,退货"
    )
    db.session.add(kb_item)
    db.session.commit()
    
    # 搜索测试
    resp = app_client.post("/api/kb/search", json={
        "query": "我要退款",
        "top_k": 3
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_message_processing(app_client):
    """测试消息处理流程"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建测试店铺
    shop = Shop(name="测试店铺", qianniu_title="千牛测试")
    db.session.add(shop)
    db.session.commit()
    
    # 创建测试消息
    message = Message(
        shop_id=shop.id,
        customer_id="test_customer",
        content="我要退款",
        source="qianniu",
        status="new"
    )
    db.session.add(message)
    db.session.commit()
    
    # 处理消息
    resp = app_client.post("/api/messages/process", json={
        "message_id": message.id
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reply" in data
    assert "source" in data
    assert "confidence" in data


def test_audit_queue(app_client):
    """测试审核队列"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建测试消息和AI回复
    shop = Shop(name="测试店铺", qianniu_title="千牛测试")
    db.session.add(shop)
    db.session.commit()
    
    message = Message(
        shop_id=shop.id,
        customer_id="test_customer",
        content="我要退款",
        source="qianniu",
        status="review"
    )
    db.session.add(message)
    db.session.commit()
    
    ai_reply = AIReply(
        message_id=message.id,
        model="stub",
        reply="请提供订单号，我们为您处理退款。",
        confidence=0.8,
        review_status="pending"
    )
    db.session.add(ai_reply)
    db.session.commit()
    
    audit_item = AuditQueueItem(
        message_id=message.id,
        status="pending"
    )
    db.session.add(audit_item)
    db.session.commit()
    
    # 获取审核队列
    resp = app_client.get("/api/audit")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["message"]["content"] == "我要退款"
    assert data[0]["ai_reply"]["reply"] == "请提供订单号，我们为您处理退款。"
    
    # 审核通过
    resp = app_client.post("/api/audit/approve", json={
        "id": audit_item.id,
        "title_kw": "千牛"
    })
    assert resp.status_code == 200
    
    # 审核拒绝
    audit_item2 = AuditQueueItem(
        message_id=message.id,
        status="pending"
    )
    db.session.add(audit_item2)
    db.session.commit()
    
    resp = app_client.post("/api/audit/reject", json={
        "id": audit_item2.id
    })
    assert resp.status_code == 200


def test_statistics_api(app_client):
    """测试统计API"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建测试数据
    shop = Shop(name="测试店铺", qianniu_title="千牛测试")
    db.session.add(shop)
    db.session.commit()
    
    # 创建测试消息
    for i in range(5):
        message = Message(
            shop_id=shop.id,
            customer_id=f"customer_{i}",
            content=f"测试消息 {i}",
            source="qianniu",
            status="answered"
        )
        db.session.add(message)
    
    db.session.commit()
    
    # 测试日统计
    resp = app_client.get("/api/statistics/daily")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "daily_data" in data
    assert "summary" in data
    
    # 测试知识库统计
    resp = app_client.get("/api/statistics/knowledge_base")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_items" in data
    assert "by_category" in data
    
    # 测试性能统计
    resp = app_client.get("/api/statistics/performance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_messages" in data
    assert "model_performance" in data


def test_user_management(app_client):
    """测试用户管理"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建用户
    user_data = {
        "username": "test_user",
        "password": "test_password",
        "role": "agent",
        "shop_id": 1
    }
    
    resp = app_client.post("/api/users", json=user_data)
    assert resp.status_code == 201
    data = resp.get_json()
    user_id = data["id"]
    
    # 获取用户列表
    resp = app_client.get("/api/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["users"]) == 2  # 包括测试用户和刚创建的用户
    
    # 更新用户
    resp = app_client.put(f"/api/users/{user_id}", json={
        "role": "admin"
    })
    assert resp.status_code == 200
    
    # 重置密码
    resp = app_client.post(f"/api/users/{user_id}/reset_password", json={
        "password": "new_password"
    })
    assert resp.status_code == 200
    
    # 删除用户
    resp = app_client.delete(f"/api/users/{user_id}")
    assert resp.status_code == 200


def test_qianniu_automation(app_client):
    """测试千牛自动化接口"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 测试获取千牛窗口列表
    resp = app_client.get("/api/qianniu/windows")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "windows" in data
    
    # 测试发送消息（需要千牛客户端运行）
    resp = app_client.post("/api/qianniu/send_test", json={
        "title_kw": "千牛",
        "message": "测试消息"
    })
    # 可能返回200或400（取决于千牛是否运行）
    assert resp.status_code in [200, 400]
    
    # 测试未读检测
    resp = app_client.post("/api/qianniu/unread_probe", json={
        "ocr_region": [800, 200, 600, 300],
        "unread_threshold": 0.02
    })
    # 可能返回200或400（取决于千牛是否运行）
    assert resp.status_code in [200, 400]
    
    # 测试OCR捕获
    resp = app_client.post("/api/qianniu/ocr_capture", json={
        "ocr_region": [800, 200, 600, 300],
        "shop_id": 1
    })
    # 可能返回200或400（取决于千牛是否运行）
    assert resp.status_code in [200, 400]
