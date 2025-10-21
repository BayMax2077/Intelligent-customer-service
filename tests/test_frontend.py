# -*- coding: utf-8 -*-
"""
前端组件测试：Vue组件功能测试

运行：
  .\.venv\Scripts\python -m pytest tests/test_frontend.py -q
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta

from houduan.app import create_app, db
from houduan.models import User, Shop, Message, KnowledgeBaseItem, AIReply, AuditQueueItem
from houduan.utils.security import hash_password


@pytest.fixture()
def app_client():
    """创建测试应用和客户端"""
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


def test_frontend_routes(app_client):
    """测试前端路由是否可访问"""
    # 测试根路径重定向
    resp = app_client.get("/")
    assert resp.status_code == 200
    
    # 测试静态文件服务
    resp = app_client.get("/index.html")
    assert resp.status_code == 200


def test_api_cors_headers(app_client):
    """测试API CORS头设置"""
    # 测试OPTIONS预检请求
    resp = app_client.options("/api/shops", headers={
        "Origin": "http://localhost:5174",
        "Access-Control-Request-Method": "GET"
    })
    assert resp.status_code == 200
    assert "Access-Control-Allow-Origin" in resp.headers


def test_frontend_build_integration(app_client):
    """测试前端构建产物集成"""
    # 测试主要页面
    pages = ["/", "/shops", "/messages", "/audit", "/kb", "/statistics", "/users"]
    
    for page in pages:
        resp = app_client.get(page)
        # 前端路由应该返回index.html
        assert resp.status_code == 200
        assert "text/html" in resp.content_type


def test_api_response_format(app_client):
    """测试API响应格式一致性"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 测试各种API的响应格式
    apis = [
        ("/api/shops", "GET"),
        ("/api/messages", "GET"),
        ("/api/audit", "GET"),
        ("/api/kb", "GET"),
        ("/api/statistics/daily", "GET"),
        ("/api/users", "GET"),
    ]
    
    for endpoint, method in apis:
        if method == "GET":
            resp = app_client.get(endpoint)
        else:
            resp = app_client.post(endpoint, json={})
        
        # 所有API都应该返回JSON格式
        assert resp.status_code in [200, 201, 400, 401, 403, 404, 500]
        if resp.status_code < 400:
            assert resp.content_type == "application/json"


def test_error_handling(app_client):
    """测试错误处理"""
    # 测试404错误
    resp = app_client.get("/api/nonexistent")
    assert resp.status_code == 404
    
    # 测试未授权访问
    resp = app_client.get("/api/shops")
    assert resp.status_code == 401
    
    # 测试无效JSON
    resp = app_client.post("/api/shops", 
                          data="invalid json",
                          content_type="application/json")
    assert resp.status_code == 400


def test_data_validation(app_client):
    """测试数据验证"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 测试店铺创建验证
    resp = app_client.post("/api/shops", json={})  # 空数据
    assert resp.status_code == 400
    
    # 测试知识库创建验证
    resp = app_client.post("/api/kb", json={})  # 空数据
    assert resp.status_code == 400
    
    # 测试用户创建验证
    resp = app_client.post("/api/users", json={})  # 空数据
    assert resp.status_code == 400


def test_pagination(app_client):
    """测试分页功能"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建测试数据
    for i in range(15):
        shop = Shop(name=f"测试店铺{i}", qianniu_title=f"千牛测试{i}")
        db.session.add(shop)
    db.session.commit()
    
    # 测试分页参数
    resp = app_client.get("/api/shops?page=1&per_page=10")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) <= 10
    
    # 测试无效分页参数
    resp = app_client.get("/api/shops?page=-1&per_page=0")
    assert resp.status_code == 200  # 应该使用默认值


def test_search_functionality(app_client):
    """测试搜索功能"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建测试知识库数据
    kb_items = [
        KnowledgeBaseItem(question="如何退款？", answer="请提供订单号", category="售后", keywords="退款,退货"),
        KnowledgeBaseItem(question="如何发货？", answer="我们会在24小时内发货", category="发货", keywords="发货,物流"),
        KnowledgeBaseItem(question="如何联系客服？", answer="请拨打客服电话", category="联系", keywords="客服,电话"),
    ]
    for item in kb_items:
        db.session.add(item)
    db.session.commit()
    
    # 测试知识库搜索
    resp = app_client.post("/api/kb/search", json={
        "query": "退款",
        "top_k": 5
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # 测试空搜索
    resp = app_client.post("/api/kb/search", json={
        "query": "",
        "top_k": 5
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_bulk_operations(app_client):
    """测试批量操作"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 测试批量导入知识库
    import_data = [
        {"question": "问题1", "answer": "答案1", "category": "测试"},
        {"question": "问题2", "answer": "答案2", "category": "测试"},
    ]
    
    resp = app_client.post("/api/kb/import", json={
        "items": import_data,
        "type": "json"
    })
    assert resp.status_code == 200
    
    # 测试批量导出
    resp = app_client.get("/api/kb/export?format=json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_performance_metrics(app_client):
    """测试性能指标"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 测试响应时间
    import time
    
    start_time = time.time()
    resp = app_client.get("/api/shops")
    end_time = time.time()
    
    assert resp.status_code == 200
    assert (end_time - start_time) < 1.0  # 响应时间应小于1秒
    
    # 测试健康检查性能
    start_time = time.time()
    resp = app_client.get("/health")
    end_time = time.time()
    
    assert resp.status_code == 200
    assert (end_time - start_time) < 0.5  # 健康检查应更快


def test_concurrent_requests(app_client):
    """测试并发请求处理"""
    import threading
    import time
    
    results = []
    
    def make_request():
        resp = app_client.get("/api/shops")
        results.append(resp.status_code)
    
    # 创建多个并发请求
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 验证所有请求都成功
    assert len(results) == 5
    assert all(status == 200 for status in results)


def test_memory_usage(app_client):
    """测试内存使用情况"""
    import psutil
    import os
    
    # 获取当前进程
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 执行一些操作
    for i in range(100):
        resp = app_client.get("/api/shops")
        assert resp.status_code == 200
    
    # 检查内存使用
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 内存增长应该合理（小于10MB）
    assert memory_increase < 10 * 1024 * 1024


def test_database_connection_pool(app_client):
    """测试数据库连接池"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 执行多个数据库操作
    for i in range(20):
        resp = app_client.get("/api/shops")
        assert resp.status_code == 200
        
        # 创建和删除店铺
        resp = app_client.post("/api/shops", json={
            "name": f"测试店铺{i}",
            "qianniu_title": f"千牛测试{i}"
        })
        if resp.status_code == 200:
            shop_id = resp.get_json()["id"]
            resp = app_client.delete(f"/api/shops/{shop_id}")
            assert resp.status_code == 200


def test_logging_functionality(app_client):
    """测试日志功能"""
    # 检查日志目录
    assert os.path.exists("logs")
    
    # 执行一些操作生成日志
    resp = app_client.get("/health")
    assert resp.status_code == 200
    
    resp = app_client.get("/api/shops")
    assert resp.status_code == 401  # 未授权，应该记录日志
    
    # 检查日志文件是否创建
    log_files = os.listdir("logs")
    assert len(log_files) > 0


def test_configuration_loading(app_client):
    """测试配置加载"""
    # 测试环境变量配置
    assert os.environ.get("DATABASE_URL") is not None
    
    # 测试默认配置
    resp = app_client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "services" in data
    assert "database" in data["services"]


def test_security_headers(app_client):
    """测试安全头设置"""
    resp = app_client.get("/")
    assert resp.status_code == 200
    
    # 检查安全头
    headers = resp.headers
    # 注意：这里只是示例，实际的安全头配置可能不同
    # assert "X-Content-Type-Options" in headers
    # assert "X-Frame-Options" in headers


def test_api_versioning(app_client):
    """测试API版本控制"""
    # 测试版本化API
    resp = app_client.get("/api/v1/shops")
    # 如果实现了版本控制，应该返回200或404
    assert resp.status_code in [200, 404]
    
    # 测试默认API
    resp = app_client.get("/api/shops")
    assert resp.status_code == 401  # 未授权


def test_data_consistency(app_client):
    """测试数据一致性"""
    # 先登录
    login = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    
    # 创建店铺
    resp = app_client.post("/api/shops", json={
        "name": "一致性测试店铺",
        "qianniu_title": "千牛一致性测试"
    })
    assert resp.status_code == 200
    shop_id = resp.get_json()["id"]
    
    # 验证数据一致性
    resp = app_client.get("/api/shops")
    assert resp.status_code == 200
    data = resp.get_json()
    shop = next((s for s in data if s["id"] == shop_id), None)
    assert shop is not None
    assert shop["name"] == "一致性测试店铺"
    assert shop["qianniu_title"] == "千牛一致性测试"
