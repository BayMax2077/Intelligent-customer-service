"""
简化版知识库管理API
使用模拟数据，避免SQLAlchemy依赖
"""

from __future__ import annotations

from datetime import datetime
from flask import request, jsonify

from . import api_bp

# 模拟知识库数据
MOCK_KB_ITEMS = [
    {"id": 1, "question": "如何退货？", "answer": "请在7天内联系客服申请退货", "category": "售后服务", "shop_id": 1, "created_at": "2025-10-21T10:00:00", "updated_at": "2025-10-21T10:00:00"},
    {"id": 2, "question": "运费如何计算？", "answer": "满99元包邮，不满99元运费10元", "category": "物流查询", "shop_id": 1, "created_at": "2025-10-21T10:01:00", "updated_at": "2025-10-21T10:01:00"},
    {"id": 3, "question": "产品保修期多长？", "answer": "产品保修期为1年", "category": "技术支持", "shop_id": 2, "created_at": "2025-10-21T10:02:00", "updated_at": "2025-10-21T10:02:00"},
    {"id": 4, "question": "如何联系客服？", "answer": "可通过在线客服或电话400-123-4567联系", "category": "产品咨询", "shop_id": None, "created_at": "2025-10-21T10:03:00", "updated_at": "2025-10-21T10:03:00"},
    {"id": 5, "question": "支付方式有哪些？", "answer": "支持微信、支付宝、银行卡支付", "category": "产品咨询", "shop_id": None, "created_at": "2025-10-21T10:04:00", "updated_at": "2025-10-21T10:04:00"},
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
    if not shop_id:
        return "全局知识库"
    return MOCK_SHOPS.get(shop_id, {}).get("name", f"未知店铺{shop_id}")


@api_bp.get("/kb")
def list_kb_items():
    """获取知识库条目列表 - 简化版"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category = request.args.get("category")
    shop_id = request.args.get("shop_id", type=int)
    search = request.args.get("search", "").strip()

    all_items = []
    for item in MOCK_KB_ITEMS:
        item_copy = item.copy()
        item_copy["shop_name"] = get_shop_name(item_copy["shop_id"])
        all_items.append(item_copy)
    
    # 分类过滤
    if category:
        all_items = [item for item in all_items if item["category"] == category]
    
    # 店铺过滤
    if shop_id is not None:
        all_items = [item for item in all_items if item["shop_id"] == shop_id]
    
    # 搜索过滤
    if search:
        all_items = [item for item in all_items if search.lower() in item["question"].lower() or search.lower() in item["answer"].lower()]

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = all_items[start:end]

    return jsonify({
        "items": paginated_items,
        "total": len(all_items),
        "page": page,
        "per_page": per_page,
        "pages": (len(all_items) + per_page - 1) // per_page,
    })


@api_bp.post("/kb")
def create_kb_item():
    """创建知识库条目 - 简化版"""
    data = request.get_json(force=True) or {}
    
    required_fields = ["question", "answer", "category"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field}_required"}), 400
    
    new_id = max(item["id"] for item in MOCK_KB_ITEMS) + 1 if MOCK_KB_ITEMS else 1
    new_item = {
        "id": new_id,
        "question": data["question"],
        "answer": data["answer"],
        "category": data["category"],
        "shop_id": data.get("shop_id"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    MOCK_KB_ITEMS.append(new_item)
    
    return jsonify({
        "id": new_item["id"],
        "message": "知识库条目创建成功"
    }), 201


@api_bp.get("/kb/<int:item_id>")
def get_kb_item(item_id):
    """获取单个知识库条目 - 简化版"""
    item = next((i for i in MOCK_KB_ITEMS if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "item_not_found"}), 404
    
    item_copy = item.copy()
    item_copy["shop_name"] = get_shop_name(item_copy["shop_id"])
    return jsonify(item_copy)


@api_bp.put("/kb/<int:item_id>")
def update_kb_item(item_id: int):
    """更新知识库条目 - 简化版"""
    data = request.get_json(force=True) or {}
    item_index = None
    for i, item in enumerate(MOCK_KB_ITEMS):
        if item["id"] == item_id:
            item_index = i
            break
    
    if item_index is None:
        return jsonify({"error": "item_not_found"}), 404
    
    if "question" in data:
        MOCK_KB_ITEMS[item_index]["question"] = data["question"]
    if "answer" in data:
        MOCK_KB_ITEMS[item_index]["answer"] = data["answer"]
    if "category" in data:
        MOCK_KB_ITEMS[item_index]["category"] = data["category"]
    if "shop_id" in data:
        MOCK_KB_ITEMS[item_index]["shop_id"] = data["shop_id"]
    
    MOCK_KB_ITEMS[item_index]["updated_at"] = datetime.now().isoformat()
    
    updated_item = MOCK_KB_ITEMS[item_index].copy()
    updated_item["shop_name"] = get_shop_name(updated_item["shop_id"])
    
    return jsonify({
        "message": "知识库条目更新成功",
        "item": updated_item
    })


@api_bp.delete("/kb/<int:item_id>")
def delete_kb_item(item_id):
    """删除知识库条目 - 简化版"""
    global MOCK_KB_ITEMS
    initial_len = len(MOCK_KB_ITEMS)
    MOCK_KB_ITEMS = [item for item in MOCK_KB_ITEMS if item["id"] != item_id]
    if len(MOCK_KB_ITEMS) == initial_len:
        return jsonify({"error": "item_not_found"}), 404
    return jsonify({"message": "知识库条目删除成功"})


@api_bp.get("/kb/categories")
def get_categories():
    """获取分类列表 - 简化版"""
    categories = list(set(item["category"] for item in MOCK_KB_ITEMS))
    return jsonify(categories)


@api_bp.post("/kb/batch-delete")
def batch_delete_kb_items():
    """批量删除知识库条目 - 简化版"""
    data = request.get_json(force=True) or {}
    item_ids = data.get("item_ids", [])
    confirm = data.get("confirm", False)
    
    if not item_ids:
        return jsonify({"error": "no_items_selected", "message": "没有选择要删除的条目"}), 400
    
    if not confirm:
        return jsonify({"error": "confirmation_required", "message": "需要确认删除操作"}), 400
    
    global MOCK_KB_ITEMS
    initial_len = len(MOCK_KB_ITEMS)
    MOCK_KB_ITEMS = [item for item in MOCK_KB_ITEMS if item["id"] not in item_ids]
    deleted_count = initial_len - len(MOCK_KB_ITEMS)
    
    return jsonify({
        "message": f"成功删除 {deleted_count} 个条目",
        "deleted_count": deleted_count
    })
