#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本：统一运行所有测试

使用方法：
  python tests/run_tests.py                    # 运行所有测试
  python tests/run_tests.py --unit              # 只运行单元测试
  python tests/run_tests.py --integration       # 只运行集成测试
  python tests/run_tests.py --frontend          # 只运行前端测试
  python tests/run_tests.py --coverage          # 运行测试并生成覆盖率报告
  python tests/run_tests.py --html              # 生成HTML测试报告
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 成功")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False


def check_environment():
    """检查测试环境"""
    print("检查测试环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    
    # 检查虚拟环境
    if not os.path.exists(".venv"):
        print("❌ 虚拟环境不存在，请先运行部署脚本")
        return False
    
    # 检查依赖
    try:
        import pytest
        print("✅ pytest已安装")
    except ImportError:
        print("❌ pytest未安装")
        return False
    
    try:
        import coverage
        print("✅ coverage已安装")
    except ImportError:
        print("⚠️  coverage未安装，覆盖率报告不可用")
    
    print("✅ 环境检查通过")
    return True


def run_unit_tests():
    """运行单元测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_api.py",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "单元测试 (API)")


def run_integration_tests():
    """运行集成测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_integration.py",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "集成测试")


def run_frontend_tests():
    """运行前端测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_frontend.py",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "前端测试")


def run_all_tests():
    """运行所有测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "所有测试")


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=houduan",
        "--cov-report=html",
        "--cov-report=term",
        "--cov-report=xml",
        "-v"
    ]
    return run_command(cmd, "测试覆盖率")


def run_tests_with_html_report():
    """运行测试并生成HTML报告"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--html=reports/test_report.html",
        "--self-contained-html",
        "-v"
    ]
    return run_command(cmd, "HTML测试报告")


def run_specific_tests(test_pattern):
    """运行特定测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/{test_pattern}",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, f"特定测试: {test_pattern}")


def run_performance_tests():
    """运行性能测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "slow",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "性能测试")


def run_quick_tests():
    """运行快速测试（排除慢测试）"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "not slow",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "快速测试")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能客服系统测试运行器")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--frontend", action="store_true", help="只运行前端测试")
    parser.add_argument("--coverage", action="store_true", help="运行测试并生成覆盖率报告")
    parser.add_argument("--html", action="store_true", help="生成HTML测试报告")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--quick", action="store_true", help="运行快速测试")
    parser.add_argument("--pattern", type=str, help="运行特定测试模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    print("智能客服系统测试运行器")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 创建报告目录
    os.makedirs("reports", exist_ok=True)
    
    success = True
    
    try:
        if args.unit:
            success = run_unit_tests()
        elif args.integration:
            success = run_integration_tests()
        elif args.frontend:
            success = run_frontend_tests()
        elif args.coverage:
            success = run_tests_with_coverage()
        elif args.html:
            success = run_tests_with_html_report()
        elif args.performance:
            success = run_performance_tests()
        elif args.quick:
            success = run_quick_tests()
        elif args.pattern:
            success = run_specific_tests(args.pattern)
        else:
            # 默认运行所有测试
            success = run_all_tests()
        
        if success:
            print("\n🎉 所有测试通过！")
            sys.exit(0)
        else:
            print("\n❌ 测试失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
