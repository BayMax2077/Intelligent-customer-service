#!/usr/bin/env python3
"""
测试简化版API功能
验证所有API端点是否正常工作
"""

import urllib.request
import urllib.parse
import json
import sys

# 配置
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

def make_request(method, url, data=None, headers=None):
    """发送HTTP请求"""
    if headers is None:
        headers = {}
    
    if data:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return response.getcode(), json.loads(response_data) if response_data else {}
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        return e.code, json.loads(error_data) if error_data else {}
    except Exception as e:
        print(f"请求失败: {e}")
        return None, None

def test_health():
    """测试健康检查"""
    print("测试健康检查...")
    status, data = make_request("GET", f"{BASE_URL}/health")
    if status == 200:
        print("健康检查通过")
        print(f"   状态: {data.get('status', 'unknown')}")
        return True
    else:
        print(f"健康检查失败: {status}")
        return False

def test_auth():
    """测试认证API"""
    print("\n测试认证API...")
    
    # 测试登录
    login_data = {"username": "admin", "password": "admin123"}
    status, data = make_request("POST", f"{API_BASE}/auth/login", login_data)
    if status == 200:
        print("登录成功")
        print(f"   用户: {data.get('user', {}).get('username', 'unknown')}")
        return True
    else:
        print(f"登录失败: {status}")
        print(f"   错误: {data.get('error', 'unknown')}")
        return False

def test_users():
    """测试用户管理API"""
    print("\n测试用户管理API...")
    
    # 测试获取用户列表
    status, data = make_request("GET", f"{API_BASE}/users")
    if status == 200:
        print("获取用户列表成功")
        print(f"   用户数量: {data.get('total', 0)}")
        return True
    else:
        print(f"获取用户列表失败: {status}")
        return False

def test_shops():
    """测试店铺管理API"""
    print("\n测试店铺管理API...")
    
    # 测试获取店铺列表
    status, data = make_request("GET", f"{API_BASE}/shops")
    if status == 200:
        print("获取店铺列表成功")
        print(f"   店铺数量: {data.get('total', 0)}")
        return True
    else:
        print(f"获取店铺列表失败: {status}")
        return False

def test_kb():
    """测试知识库API"""
    print("\n测试知识库API...")
    
    # 测试获取知识库条目
    status, data = make_request("GET", f"{API_BASE}/kb")
    if status == 200:
        print("获取知识库条目成功")
        print(f"   条目数量: {data.get('total', 0)}")
        return True
    else:
        print(f"获取知识库条目失败: {status}")
        return False

def test_messages():
    """测试消息管理API"""
    print("\n测试消息管理API...")
    
    # 测试获取消息列表
    status, data = make_request("GET", f"{API_BASE}/messages")
    if status == 200:
        print("获取消息列表成功")
        print(f"   消息数量: {data.get('total', 0)}")
        return True
    else:
        print(f"获取消息列表失败: {status}")
        return False

def test_statistics():
    """测试统计报表API"""
    print("\n测试统计报表API...")
    
    # 测试获取日统计数据
    status, data = make_request("GET", f"{API_BASE}/statistics/daily")
    if status == 200:
        print("获取日统计数据成功")
        print(f"   数据点数量: {len(data.get('daily_data', []))}")
        return True
    else:
        print(f"获取日统计数据失败: {status}")
        return False

def main():
    """主测试函数"""
    print("开始测试简化版API功能...")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health),
        ("认证API", test_auth),
        ("用户管理API", test_users),
        ("店铺管理API", test_shops),
        ("知识库API", test_kb),
        ("消息管理API", test_messages),
        ("统计报表API", test_statistics),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！简化版API工作正常。")
        return 0
    else:
        print("部分测试失败，需要检查API实现。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
