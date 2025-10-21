from __future__ import annotations

from flask import request, jsonify
from flask_login import login_required

from . import api_bp
from ..utils.security import require_roles
from ..services.qianniu_monitor import (
    list_windows_by_title,
    activate_window_by_title,
    send_text_in_active_window,
    screenshot_region,
    ocr_text,
    unread_score,
)
from ..app import db
from ..models import Message, Shop


@api_bp.get("/qianniu/windows")
@login_required
def list_windows():
    keyword = request.args.get("q", "千牛")
    return jsonify(list_windows_by_title(keyword))


@api_bp.post("/qianniu/send_test")
@login_required
@require_roles("superadmin", "admin")
def send_test():
    data = request.get_json(force=True) or {}
    title_kw = data.get("title_kw", "千牛")
    text = data.get("text", "[自动化探针测试]")
    ok = activate_window_by_title(title_kw)
    if not ok:
        return jsonify({"ok": False, "error": "window_not_found"}), 404
    send_text_in_active_window(text)
    return jsonify({"ok": True})


@api_bp.post("/qianniu/unread_probe")
@login_required
def unread_probe():
    data = request.get_json(force=True) or {}
    # 默认探测屏幕左下角 300x300 像素区域（可在前端配置）
    region = data.get("region", [0, 700, 300, 300])
    img = screenshot_region(tuple(region))
    score = unread_score(img)
    return jsonify({"score": round(score, 4)})


@api_bp.post("/qianniu/ocr_capture")
@login_required
def ocr_capture():
    data = request.get_json(force=True) or {}
    region = data.get("region")
    shop_id = data.get("shop_id")
    customer_id = data.get("customer_id", "unknown")
    if not region or not isinstance(region, list) or len(region) != 4:
        return jsonify({"error": "invalid_region"}), 400
    if not shop_id:
        return jsonify({"error": "shop_id_required"}), 400
    # 截图 + OCR
    img = screenshot_region(tuple(region))
    text = ocr_text(img)
    # 入库
    msg = Message(shop_id=int(shop_id), customer_id=str(customer_id), content=text or "", source="qianniu", status="new")
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id, "content_len": len(text or ""), "empty": not bool(text)})


