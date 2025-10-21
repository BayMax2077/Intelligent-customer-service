"""
千牛 UI 自动化探针（原型）

功能：
- 列出匹配窗口标题的顶级窗口
- 激活窗口并发送测试文本（用于验证自动化可行性）

注意：
- 需在 Windows 上运行，且已安装 pywin32、pyautogui
- 运行前请确保千牛客户端已登录并可见
"""

from __future__ import annotations

import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Set

import pyautogui
import win32gui
import win32con
from PIL import Image

# 可选OCR依赖（PaddleOCR），未安装时降级为空实现
try:
    from paddleocr import PaddleOCR  # type: ignore
    _ocr_client: Optional[PaddleOCR] = None
except Exception:  # pragma: no cover - 环境未装OCR
    PaddleOCR = None  # type: ignore
    _ocr_client = None

# 消息去重缓存（内存中，重启后清空）
_message_cache: Set[str] = set()
_cache_cleanup_time = datetime.now()


def list_windows_by_title(keyword: str) -> List[str]:
    titles: List[str] = []

    def _enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and keyword.lower() in title.lower():
                titles.append(title)

    win32gui.EnumWindows(_enum_handler, None)
    return sorted(set(titles))


def activate_window_by_title(title_keyword: str) -> bool:
    target_hwnd = None

    def _enum_handler(hwnd, _):
        nonlocal target_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and title_keyword.lower() in title.lower():
                target_hwnd = hwnd

    win32gui.EnumWindows(_enum_handler, None)
    if not target_hwnd:
        return False

    # 置顶并激活
    win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(target_hwnd)
    time.sleep(0.3)
    return True


def send_text_in_active_window(text: str) -> None:
    # 将焦点窗口作为输入目标，输入并回车
    pyautogui.typewrite(text, interval=0.02)
    pyautogui.press('enter')


def screenshot_region(region: Tuple[int, int, int, int]) -> Image.Image:
    """对屏幕区域截图。

    region: (x, y, width, height)
    """
    x, y, w, h = region
    shot = pyautogui.screenshot(region=(x, y, w, h))
    return shot


def ocr_text_with_retry(image: Image.Image, max_retries: int = 3) -> str:
    """对截图进行OCR，带重试机制。

    若未安装 PaddleOCR，将返回空字符串并提示调用方按需安装。
    """
    global _ocr_client
    if PaddleOCR is None:
        return ""
    
    for attempt in range(max_retries):
        try:
            if _ocr_client is None:
                # 初始化中文模型，关闭日志
                _ocr_client = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            
            result = _ocr_client.ocr(image, cls=True)
            lines: List[str] = []
            for page in result or []:
                for _, (text, conf) in page:
                    if text and conf > 0.5:  # 置信度过滤
                        lines.append(text)
            
            if lines:  # 成功识别到文本
                return "\n".join(lines)
            elif attempt < max_retries - 1:  # 还有重试机会
                time.sleep(0.5)  # 短暂等待后重试
                continue
            else:
                return ""  # 所有重试都失败
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 异常后等待更长时间
                _ocr_client = None  # 重置客户端
                continue
            else:
                # 最后一次尝试失败，记录错误但不抛出异常
                return ""


def ocr_text(image: Image.Image) -> str:
    """对截图进行OCR，尽可能返回文本（保持向后兼容）"""
    return ocr_text_with_retry(image)


def unread_score(image: Image.Image) -> float:
    """简单未读提示评分：统计红色像素占比。

    该评分用于辅助判断未读红点是否出现，范围[0,1]。
    """
    img = image.convert('RGB')
    width, height = img.size
    total = width * height
    red_like = 0
    for px in img.getdata():
        r, g, b = px
        if r > 180 and g < 80 and b < 80:  # 简化红点阈值
            red_like += 1
    return red_like / max(total, 1)


def generate_message_hash(text: str, shop_id: int) -> str:
    """生成消息内容的哈希值用于去重"""
    # 清理文本：去除多余空白、标点符号
    cleaned_text = "".join(c for c in text if c.isalnum() or c.isspace()).strip()
    # 生成哈希：内容 + 店铺ID + 时间窗口（5分钟）
    time_window = datetime.now().replace(minute=(datetime.now().minute // 5) * 5, second=0, microsecond=0)
    hash_input = f"{cleaned_text}:{shop_id}:{time_window.isoformat()}"
    return hashlib.md5(hash_input.encode('utf-8')).hexdigest()


def is_duplicate_message(text: str, shop_id: int) -> bool:
    """检查消息是否重复"""
    global _message_cache, _cache_cleanup_time
    
    # 定期清理缓存（每10分钟清理一次）
    now = datetime.now()
    if now - _cache_cleanup_time > timedelta(minutes=10):
        _message_cache.clear()
        _cache_cleanup_time = now
    
    if not text or not text.strip():
        return True
    
    message_hash = generate_message_hash(text, shop_id)
    
    if message_hash in _message_cache:
        return True
    
    # 添加到缓存
    _message_cache.add(message_hash)
    return False


def poll_and_capture(shop_config: dict, shop_id: int = 1) -> Tuple[float, str]:
    """根据店铺配置进行未读检测与OCR采集。

    shop_config keys:
      - ocr_region: [x,y,w,h]
      - unread_threshold: float 0~1
    返回: (score, text)
    """
    region = tuple(shop_config.get("ocr_region", [0, 700, 300, 300]))
    threshold = float(shop_config.get("unread_threshold", 0.02))
    img = screenshot_region(region)
    score = unread_score(img)
    if score >= threshold:
        # 认为有未读，进行更大区域OCR
        chat_region = tuple(shop_config.get("chat_region", region))
        text = ocr_text(screenshot_region(chat_region))
        
        # 去重检查
        if is_duplicate_message(text, shop_id):
            return score, ""  # 重复消息，返回空文本
        
        return score, text or ""
    return score, ""


