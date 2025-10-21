#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Flask路由注册
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'houduan'))

from houduan.app import create_app

def test_routes():
    """测试路由注册"""
    app = create_app()
    
    print("Flask应用路由列表:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
    
    print("\n查找batch相关路由:")
    for rule in app.url_map.iter_rules():
        if 'batch' in rule.rule:
            print(f"  {rule.methods} {rule.rule}")

if __name__ == "__main__":
    test_routes()
