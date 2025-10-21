#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试路由注册问题
"""

import urllib.request
import urllib.parse
import json

def test_route_registration():
    """测试路由注册"""
    base_url = "http://127.0.0.1:5000"
    
    print("测试路由注册...")
    
    # 测试不同的路由
    routes_to_test = [
        ("GET", "/api/kb"),
        ("GET", "/api/kb/categories"),
        ("GET", "/api/kb/template"),
        ("DELETE", "/api/kb/batch"),
        ("POST", "/api/kb/batch"),
    ]
    
    for method, route in routes_to_test:
        try:
            request = urllib.request.Request(f"{base_url}{route}", method=method)
            with urllib.request.urlopen(request) as response:
                status = response.status
                print(f"  {method} {route} -> {status}")
        except urllib.error.HTTPError as e:
            print(f"  {method} {route} -> {e.code} ({e.reason})")
        except Exception as e:
            print(f"  {method} {route} -> 错误: {e}")

if __name__ == "__main__":
    test_route_registration()
