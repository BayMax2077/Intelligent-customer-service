#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试路由注册
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'houduan'))

def test_import():
    """测试导入"""
    try:
        from houduan.api.kb import api_bp
        print("✅ 成功导入 api_bp")
        
        # 检查路由
        for rule in api_bp.url_map.iter_rules():
            print(f"  {rule.methods} {rule.rule}")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

if __name__ == "__main__":
    test_import()
