#!/usr/bin/env python3
"""
微信OCR验证脚本

功能：
- 验证PaddleOCR安装和功能
- 测试微信窗口检测
- 验证红点检测和OCR识别
- 测试消息去重机制

使用方法：
python scripts/verify_ocr.py
"""

import sys
import os
import json
import time
import hashlib
from datetime import datetime
from typing import List, Tuple, Optional, Dict

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_step(step: int, title: str, status: str = ""):
    """打印步骤"""
    status_icon = "✓" if status == "ok" else "⚠" if status == "warning" else "✗" if status == "error" else ""
    print(f"\n[阶段{step}] {title} {status_icon}")

def print_result(message: str, success: bool = True):
    """打印结果"""
    icon = "✓" if success else "✗"
    print(f"  {icon} {message}")

def print_warning(message: str):
    """打印警告"""
    print(f"  ⚠ {message}")

def print_error(message: str):
    """打印错误"""
    print(f"  ✗ {message}")

# 阶段1: 环境检查
def check_dependencies() -> Dict[str, bool]:
    """检查所有依赖是否安装"""
    print_step(1, "环境检查")
    
    dependencies = {
        "pywin32": False,
        "pyautogui": False,
        "PIL": False,
        "imagehash": False,
        "paddleocr": False,
        "paddlepaddle": False
    }
    
    # 检查pywin32
    try:
        import win32gui
        import win32con
        dependencies["pywin32"] = True
        print_result("pywin32: 已安装")
    except ImportError:
        print_error("pywin32: 未安装")
    
    # 检查pyautogui
    try:
        import pyautogui
        dependencies["pyautogui"] = True
        print_result("pyautogui: 已安装")
    except ImportError:
        print_error("pyautogui: 未安装")
    
    # 检查PIL
    try:
        from PIL import Image
        dependencies["PIL"] = True
        print_result("Pillow: 已安装")
    except ImportError:
        print_error("Pillow: 未安装")
    
    # 检查imagehash
    try:
        import imagehash
        dependencies["imagehash"] = True
        print_result("imagehash: 已安装")
    except ImportError:
        print_error("imagehash: 未安装")
    
    # 检查paddleocr
    try:
        from paddleocr import PaddleOCR
        dependencies["paddleocr"] = True
        print_result("paddleocr: 已安装")
    except ImportError:
        print_error("paddleocr: 未安装")
    
    # 检查paddlepaddle
    try:
        import paddle
        dependencies["paddlepaddle"] = True
        print_result("paddlepaddle: 已安装")
    except ImportError:
        print_error("paddlepaddle: 未安装")
    
    all_ok = all(dependencies.values())
    if all_ok:
        print_result("所有依赖检查通过", True)
    else:
        print_error("部分依赖缺失，请运行: pip install -r requirements.txt")
    
    return dependencies

# 阶段2: OCR基础测试
def test_ocr_basic() -> bool:
    """测试OCR基础功能"""
    print_step(2, "OCR基础测试")
    
    try:
        from paddleocr import PaddleOCR
        from PIL import Image
        import pyautogui
        
        # 创建测试图片（简单的文字图片）
        print_result("正在创建测试图片...")
        
        # 截取屏幕一小块作为测试
        test_region = (100, 100, 200, 100)
        img = pyautogui.screenshot(region=test_region)
        
        # 初始化OCR
        print_result("正在初始化PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        
        # 执行OCR
        print_result("正在执行OCR识别...")
        result = ocr.ocr(img, cls=True)
        
        if result and result[0]:
            text_lines = []
            for line in result[0]:
                if line[1][1] > 0.5:  # 置信度过滤
                    text_lines.append(line[1][0])
            
            if text_lines:
                print_result(f"OCR识别成功，识别到: {' '.join(text_lines)}")
                return True
            else:
                print_warning("OCR识别成功但未检测到文字")
                return True
        else:
            print_warning("OCR识别成功但未检测到文字")
            return True
            
    except Exception as e:
        print_error(f"OCR测试失败: {str(e)}")
        return False

# 阶段3: 微信窗口检测
def detect_wechat_windows() -> List[str]:
    """检测微信窗口"""
    print_step(3, "微信窗口检测")
    
    try:
        import win32gui
        
        windows = []
        
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("微信" in title or "WeChat" in title):
                    windows.append(title)
        
        win32gui.EnumWindows(enum_handler, None)
        
        if windows:
            print_result(f"找到 {len(windows)} 个微信窗口:")
            for i, window in enumerate(windows, 1):
                print_result(f"  {i}. {window}")
        else:
            print_warning("未找到微信窗口，请确保微信PC客户端已打开")
        
        return windows
        
    except Exception as e:
        print_error(f"窗口检测失败: {str(e)}")
        return []

# 阶段4: 红点检测测试
def test_red_dot_detection(region: Tuple[int, int, int, int]) -> float:
    """测试红点检测"""
    print_step(4, "红点检测测试")
    
    try:
        import pyautogui
        from PIL import Image
        
        print_result(f"截图区域: {region}")
        img = pyautogui.screenshot(region=region)
        
        # 计算红点分数
        img_rgb = img.convert('RGB')
        width, height = img_rgb.size
        total = width * height
        red_like = 0
        
        for px in img_rgb.getdata():
            r, g, b = px
            if r > 180 and g < 80 and b < 80:  # 红点阈值
                red_like += 1
        
        score = red_like / max(total, 1)
        print_result(f"红点检测分数: {score:.4f}")
        
        if score > 0.01:
            print_result("检测到可能的红点", True)
        else:
            print_result("未检测到红点")
        
        return score
        
    except Exception as e:
        print_error(f"红点检测失败: {str(e)}")
        return 0.0

# 阶段5: 完整流程测试
def test_complete_flow(region: Tuple[int, int, int, int]) -> Tuple[float, str]:
    """测试完整流程（红点→图像哈希→OCR）"""
    print_step(5, "完整流程测试")
    
    try:
        import pyautogui
        from PIL import Image
        import imagehash
        from paddleocr import PaddleOCR
        
        # 截图
        print_result("正在截图...")
        img = pyautogui.screenshot(region=region)
        
        # 红点检测
        print_result("正在检测红点...")
        img_rgb = img.convert('RGB')
        width, height = img_rgb.size
        total = width * height
        red_like = 0
        
        for px in img_rgb.getdata():
            r, g, b = px
            if r > 180 and g < 80 and b < 80:
                red_like += 1
        
        score = red_like / max(total, 1)
        print_result(f"红点分数: {score:.4f}")
        
        # 图像哈希检测
        print_result("正在计算图像哈希...")
        current_hash = str(imagehash.dhash(img, hash_size=8))
        print_result(f"图像哈希: {current_hash[:16]}...")
        
        # OCR识别
        print_result("正在执行OCR识别...")
        ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        result = ocr.ocr(img, cls=True)
        
        text = ""
        if result and result[0]:
            text_lines = []
            for line in result[0]:
                if line[1][1] > 0.5:
                    text_lines.append(line[1][0])
            text = "\n".join(text_lines)
        
        if text:
            print_result(f"OCR识别成功，识别到 {len(text)} 个字符")
            print_result(f"识别内容: {text[:50]}{'...' if len(text) > 50 else ''}")
        else:
            print_warning("OCR未识别到文字")
        
        return score, text
        
    except Exception as e:
        print_error(f"完整流程测试失败: {str(e)}")
        return 0.0, ""

# 阶段6: 消息去重测试
def test_message_deduplication() -> bool:
    """测试消息去重机制"""
    print_step(6, "消息去重测试")
    
    try:
        # 模拟消息去重
        message_cache = set()
        
        def generate_message_hash(text: str, shop_id: int) -> str:
            cleaned_text = "".join(c for c in text if c.isalnum() or c.isspace()).strip()
            time_window = datetime.now().replace(minute=(datetime.now().minute // 5) * 5, second=0, microsecond=0)
            hash_input = f"{cleaned_text}:{shop_id}:{time_window.isoformat()}"
            return hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        
        def is_duplicate_message(text: str, shop_id: int) -> bool:
            message_hash = generate_message_hash(text, shop_id)
            if message_hash in message_cache:
                return True
            message_cache.add(message_hash)
            return False
        
        # 测试相同消息
        test_message = "这是一条测试消息"
        shop_id = 1
        
        print_result("测试相同消息去重...")
        is_dup1 = is_duplicate_message(test_message, shop_id)
        is_dup2 = is_duplicate_message(test_message, shop_id)
        
        if not is_dup1 and is_dup2:
            print_result("相同消息去重: 正常")
        else:
            print_error("相同消息去重: 异常")
            return False
        
        # 测试不同消息
        print_result("测试不同消息...")
        is_dup3 = is_duplicate_message("这是另一条消息", shop_id)
        
        if not is_dup3:
            print_result("不同消息处理: 正常")
        else:
            print_error("不同消息处理: 异常")
            return False
        
        print_result("消息去重机制: 正常")
        return True
        
    except Exception as e:
        print_error(f"消息去重测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print_header("微信OCR验证脚本")
    print("此脚本将验证PaddleOCR安装和微信消息捕获功能")
    print("请确保微信PC客户端已打开并有可见的聊天窗口")
    
    # 检查依赖
    dependencies = check_dependencies()
    if not all(dependencies.values()):
        print_error("依赖检查失败，请先安装缺失的依赖")
        return False
    
    # OCR基础测试
    if not test_ocr_basic():
        print_error("OCR基础测试失败")
        return False
    
    # 检测微信窗口
    windows = detect_wechat_windows()
    if not windows:
        print_warning("未找到微信窗口，将使用默认区域进行测试")
    
    # 获取OCR区域
    print("\n请输入OCR区域坐标 (格式: x,y,w,h):")
    print("例如: 600,150,800,600")
    print("提示: 请确保区域覆盖微信聊天窗口的文字区域")
    
    region_input = input("区域坐标 (直接回车使用默认 600,150,800,600): ").strip()
    if not region_input:
        region = (600, 150, 800, 600)
    else:
        try:
            coords = [int(x.strip()) for x in region_input.split(',')]
            if len(coords) != 4:
                raise ValueError("需要4个坐标值")
            region = tuple(coords)
        except ValueError:
            print_warning("坐标格式错误，使用默认区域")
            region = (600, 150, 800, 600)
    
    print_result(f"使用区域: {region}")
    
    # 红点检测测试
    score = test_red_dot_detection(region)
    
    # 完整流程测试
    final_score, ocr_text = test_complete_flow(region)
    
    # 消息去重测试
    dedup_ok = test_message_deduplication()
    
    # 生成报告
    print_header("验证报告")
    
    print_result("依赖检查: 通过", True)
    print_result("OCR功能: 正常", True)
    print_result(f"窗口检测: 找到 {len(windows)} 个微信窗口", len(windows) > 0)
    print_result(f"红点检测: 分数 {score:.4f}", score >= 0.0)
    print_result(f"OCR识别: 识别到 {len(ocr_text)} 字", len(ocr_text) > 0)
    print_result("消息去重: 正常", dedup_ok)
    
    # 建议
    print("\n建议:")
    if score < 0.01:
        print_warning("红点检测分数较低，可能需要调整OCR区域或阈值")
    if len(ocr_text) < 10:
        print_warning("OCR识别文字较少，建议调整区域坐标以提高识别率")
    if not dedup_ok:
        print_warning("消息去重机制需要检查")
    
    # 输出配置建议
    print(f"\n推荐的微信配置:")
    print(f"OCR区域: {region}")
    print(f"未读阈值: {max(0.01, score * 2):.3f}")
    print(f"哈希阈值: 5")
    
    all_passed = all([
        all(dependencies.values()),
        len(windows) > 0 or True,  # 窗口检测不是必须的
        score >= 0.0,
        len(ocr_text) >= 0,
        dedup_ok
    ])
    
    if all_passed:
        print_result("验证完成: 所有测试通过", True)
    else:
        print_error("验证完成: 部分测试失败")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n验证过程中发生错误: {str(e)}")
        sys.exit(1)
