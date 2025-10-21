"""
简化版消息管理API
使用模拟数据，避免SQLAlchemy依赖
"""

from __future__ import annotations

from datetime import datetime
from flask import request, jsonify

from . import api_bp

# 模拟消息数据
MOCK_MESSAGES = [
    {"id": 1, "content": "你好，我想了解一下这个产品的价格", "status": "pending", "shop_id": 1, "created_at": "2025-10-21T10:00:00", "updated_at": "2025-10-21T10:00:00"},
    {"id": 2, "content": "请问什么时候发货？", "status": "processed", "shop_id": 1, "created_at": "2025-10-21T10:01:00", "updated_at": "2025-10-21T10:01:00"},
    {"id": 3, "content": "这个产品有保修吗？", "status": "pending", "shop_id": 2, "created_at": "2025-10-21T10:02:00", "updated_at": "2025-10-21T10:02:00"},
    {"id": 4, "content": "如何申请退货？", "status": "processed", "shop_id": 2, "created_at": "2025-10-21T10:03:00", "updated_at": "2025-10-21T10:03:00"},
    {"id": 5, "content": "运费是多少？", "status": "pending", "shop_id": 3, "created_at": "2025-10-21T10:04:00", "updated_at": "2025-10-21T10:04:00"},
]

# 模拟店铺数据
MOCK_SHOPS = {
    1: {"id": 1, "name": "测试店铺A"},
    2: {"id": 2, "name": "测试店铺B"},
    3: {"id": 3, "name": "测试店铺C"},
    4: {"id": 4, "name": "测试店铺D"},
}

def get_shop_name(shop_id):
    """获取店铺名称"""
    return MOCK_SHOPS.get(shop_id, {}).get("name", f"未知店铺{shop_id}")


@api_bp.get("/messages")
def list_messages():
    """获取消息列表 - 简化版"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")
    shop_id = request.args.get("shop_id", type=int)
    search = request.args.get("search", "").strip()

    all_messages = []
    for message in MOCK_MESSAGES:
        message_copy = message.copy()
        message_copy["shop_name"] = get_shop_name(message_copy["shop_id"])
        all_messages.append(message_copy)
    
    # 状态过滤
    if status:
        all_messages = [msg for msg in all_messages if msg["status"] == status]
    
    # 店铺过滤
    if shop_id is not None:
        all_messages = [msg for msg in all_messages if msg["shop_id"] == shop_id]
    
    # 搜索过滤
    if search:
        all_messages = [msg for msg in all_messages if search.lower() in msg["content"].lower()]

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_messages = all_messages[start:end]

    return jsonify({
        "messages": paginated_messages,
        "total": len(all_messages),
        "page": page,
        "per_page": per_page,
        "pages": (len(all_messages) + per_page - 1) // per_page,
    })


@api_bp.post("/messages")
def create_message():
    """创建消息 - 简化版"""
    data = request.get_json(force=True) or {}
    
    required_fields = ["content", "shop_id"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field}_required"}), 400
    
    new_id = max(msg["id"] for msg in MOCK_MESSAGES) + 1 if MOCK_MESSAGES else 1
    new_message = {
        "id": new_id,
        "content": data["content"],
        "status": data.get("status", "pending"),
        "shop_id": data["shop_id"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    MOCK_MESSAGES.append(new_message)
    
    return jsonify({
        "id": new_message["id"],
        "message": "消息创建成功"
    }), 201


@api_bp.get("/messages/<int:message_id>")
def get_message(message_id):
    """获取单个消息 - 简化版"""
    message = next((m for m in MOCK_MESSAGES if m["id"] == message_id), None)
    if not message:
        return jsonify({"error": "message_not_found"}), 404
    
    message_copy = message.copy()
    message_copy["shop_name"] = get_shop_name(message_copy["shop_id"])
    return jsonify(message_copy)


@api_bp.put("/messages/<int:message_id>")
def update_message(message_id: int):
    """更新消息 - 简化版"""
    data = request.get_json(force=True) or {}
    message_index = None
    for i, message in enumerate(MOCK_MESSAGES):
        if message["id"] == message_id:
            message_index = i
            break
    
    if message_index is None:
        return jsonify({"error": "message_not_found"}), 404
    
    if "content" in data:
        MOCK_MESSAGES[message_index]["content"] = data["content"]
    if "status" in data:
        MOCK_MESSAGES[message_index]["status"] = data["status"]
    if "shop_id" in data:
        MOCK_MESSAGES[message_index]["shop_id"] = data["shop_id"]
    
    MOCK_MESSAGES[message_index]["updated_at"] = datetime.now().isoformat()
    
    return jsonify({
        "message": "消息更新成功",
        "data": MOCK_MESSAGES[message_index]
    })


@api_bp.delete("/messages/<int:message_id>")
def delete_message(message_id):
    """删除消息 - 简化版"""
    global MOCK_MESSAGES
    initial_len = len(MOCK_MESSAGES)
    MOCK_MESSAGES = [msg for msg in MOCK_MESSAGES if msg["id"] != message_id]
    if len(MOCK_MESSAGES) == initial_len:
        return jsonify({"error": "message_not_found"}), 404
    return jsonify({"message": "消息删除成功"})
