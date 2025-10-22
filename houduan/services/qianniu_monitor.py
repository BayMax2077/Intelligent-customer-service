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
from typing import List, Optional, Tuple, Set, Dict

import pyautogui
import win32gui
import win32con
from PIL import Image
import imagehash

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

# 图像哈希缓存：存储区域的最近哈希值
_region_hash_cache: Dict[str, str] = {}
_ocr_result_cache: Dict[str, Tuple[str, datetime]] = {}  # 哈希 -> (文本, 时间)


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
    """三层混合检测：红点检测 → 区域哈希对比 → OCR识别
    
    shop_config keys:
      - ocr_region: [x,y,w,h] OCR检测区域
      - unread_threshold: float 0~1 未读阈值
      - hash_threshold: int (可选) 图像变化敏感度，默认5
    
    返回: (score, text)
    """
    region = tuple(shop_config.get("ocr_region", [0, 700, 300, 300]))
    threshold = float(shop_config.get("unread_threshold", 0.02))
    hash_threshold = int(shop_config.get("hash_threshold", 5))
    
    # 第一层：红点检测（最快）
    img = screenshot_region(region)
    score = unread_score(img)
    
    if score < threshold:
        # 没有未读标识，直接返回
        return score, ""
    
    # 第二层：区域哈希对比（判断内容是否变化）
    cache_key = get_region_cache_key(shop_id, region)
    
    if not has_region_changed(img, cache_key, hash_threshold):
        # 图像无变化，无需OCR
        return score, ""
    
    # 第三层：OCR识别（仅在内容变化时执行）
    chat_region = tuple(shop_config.get("chat_region", region))
    chat_img = screenshot_region(chat_region)
    
    # 使用带缓存的OCR
    text = ocr_text_cached(chat_img)
    
    # 去重检查
    if is_duplicate_message(text, shop_id):
        return score, ""  # 重复消息，返回空文本
    
    return score, text or ""


def calculate_image_hash(image: Image.Image) -> str:
    """计算图像的感知哈希值用于快速对比"""
    # 使用差异哈希（dHash），对图像变化敏感
    return str(imagehash.dhash(image, hash_size=8))


def get_region_cache_key(shop_id: int, region: Tuple[int, int, int, int]) -> str:
    """生成区域缓存键"""
    return f"shop_{shop_id}_region_{region[0]}_{region[1]}_{region[2]}_{region[3]}"


def has_region_changed(image: Image.Image, cache_key: str, 
                       hash_threshold: int = 5) -> bool:
    """检测区域图像是否发生变化
    
    Args:
        image: 当前截图
        cache_key: 缓存键
        hash_threshold: 哈希差异阈值（默认5，值越小越敏感）
    
    Returns:
        True if 图像有变化，False otherwise
    """
    global _region_hash_cache
    
    current_hash = calculate_image_hash(image)
    
    if cache_key not in _region_hash_cache:
        # 首次检测，记录并返回True
        _region_hash_cache[cache_key] = current_hash
        return True
    
    # 计算哈希差异
    last_hash = _region_hash_cache[cache_key]
    hash_diff = imagehash.hex_to_hash(current_hash) - imagehash.hex_to_hash(last_hash)
    
    if hash_diff > hash_threshold:
        # 图像有显著变化，更新缓存
        _region_hash_cache[cache_key] = current_hash
        return True
    
    return False


def get_cached_ocr_result(image_hash: str, max_age_seconds: int = 60) -> Optional[str]:
    """从缓存获取OCR结果"""
    global _ocr_result_cache
    
    if image_hash in _ocr_result_cache:
        text, timestamp = _ocr_result_cache[image_hash]
        # 检查缓存是否过期
        if (datetime.now() - timestamp).total_seconds() < max_age_seconds:
            return text
        else:
            # 过期，删除缓存
            del _ocr_result_cache[image_hash]
    
    return None


def cache_ocr_result(image_hash: str, text: str):
    """缓存OCR结果"""
    global _ocr_result_cache
    
    # 限制缓存大小，超过100条时清理最旧的
    if len(_ocr_result_cache) > 100:
        # 按时间排序，删除最旧的20条
        sorted_cache = sorted(_ocr_result_cache.items(), 
                            key=lambda x: x[1][1])
        for key, _ in sorted_cache[:20]:
            del _ocr_result_cache[key]
    
    _ocr_result_cache[image_hash] = (text, datetime.now())


def ocr_text_cached(image: Image.Image) -> str:
    """带缓存的OCR识别"""
    # 计算图像哈希
    image_hash = calculate_image_hash(image)
    
    # 尝试从缓存获取
    cached_result = get_cached_ocr_result(image_hash)
    if cached_result is not None:
        return cached_result
    
    # 缓存未命中，执行OCR
    text = ocr_text_with_retry(image)
    
    # 缓存结果
    if text:
        cache_ocr_result(image_hash, text)
    
    return text


def cleanup_caches():
    """清理所有缓存"""
    global _message_cache, _region_hash_cache, _ocr_result_cache
    global _cache_cleanup_time
    
    now = datetime.now()
    
    # 清理消息缓存（每10分钟）
    if now - _cache_cleanup_time > timedelta(minutes=10):
        _message_cache.clear()
        _cache_cleanup_time = now
    
    # 清理过期的OCR结果缓存（每5分钟）
    expired_keys = []
    for img_hash, (_, timestamp) in _ocr_result_cache.items():
        if (now - timestamp).total_seconds() > 300:  # 5分钟过期
            expired_keys.append(img_hash)
    
    for key in expired_keys:
        del _ocr_result_cache[key]
    
    # 清理区域哈希缓存（如果超过50个店铺区域）
    if len(_region_hash_cache) > 50:
        _region_hash_cache.clear()


