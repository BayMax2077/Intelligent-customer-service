#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能修复
"""

import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_login(username, password):
    """测试登录功能"""
    print(f"=== 测试登录: {username} ===")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    url = f"{BASE_URL}/auth/login"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'TestScript/1.0'
    }
    
    data_encoded = json.dumps(login_data).encode('utf-8')
    req = urllib.request.Request(url, data=data_encoded, method='POST', headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            print(f"登录响应: {response_data}")
            print(f"状态码: {response.status}")
            
            if response.status == 200 and response_data.get("ok"):
                print("登录成功！")
                user_info = response_data.get("user", {})
                print(f"用户信息: ID={user_info.get('id')}, 用户名={user_info.get('username')}, 角色={user_info.get('role')}")
                return True
            else:
                print("登录失败！")
                return False
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"登录错误: {e.code}")
        print(f"错误内容: {error_data}")
        return False
    except Exception as e:
        print(f"登录异常: {e}")
        return False

def test_logout():
    """测试登出功能"""
    print("\n=== 测试登出 ===")
    
    url = f"{BASE_URL}/auth/logout"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'TestScript/1.0'
    }
    
    req = urllib.request.Request(url, data=b'', method='POST', headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            print(f"登出响应: {response_data}")
            print(f"状态码: {response.status}")
            
            if response.status == 200 and response_data.get("ok"):
                print("登出成功！")
                return True
            else:
                print("登出失败！")
                return False
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"登出错误: {e.code}")
        print(f"错误内容: {error_data}")
        return False
    except Exception as e:
        print(f"登出异常: {e}")
        return False

def main():
    print("登录功能修复测试")
    print("=" * 40)
    
    # 测试正确的用户名和密码
    print("1. 测试正确登录")
    test_login("admin", "admin123")
    
    print("\n2. 测试错误密码")
    test_login("admin", "wrongpassword")
    
    print("\n3. 测试不存在的用户")
    test_login("nonexistent", "password")
    
    print("\n4. 测试其他用户")
    test_login("superadmin", "superadmin123")
    
    print("\n5. 测试登出")
    test_logout()
    
    print("\n测试总结:")
    print("- 如果admin/admin123登录成功，说明修复成功")
    print("- 如果错误密码返回401，说明验证正常")
    print("- 如果登出成功，说明会话管理正常")

if __name__ == "__main__":
    main()
