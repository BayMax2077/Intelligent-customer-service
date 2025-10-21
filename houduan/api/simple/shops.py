"""
简化版店铺管理API
使用模拟数据，避免SQLAlchemy依赖
"""

from __future__ import annotations

from datetime import datetime
from flask import request, jsonify

from . import api_bp

# 模拟店铺数据
MOCK_SHOPS = [
    {"id": 1, "name": "测试店铺A", "description": "测试店铺A的描述", "status": "active", "created_at": "2025-10-21T10:00:00", "updated_at": "2025-10-21T10:00:00"},
    {"id": 2, "name": "测试店铺B", "description": "测试店铺B的描述", "status": "active", "created_at": "2025-10-21T10:01:00", "updated_at": "2025-10-21T10:01:00"},
    {"id": 3, "name": "测试店铺C", "description": "测试店铺C的描述", "status": "inactive", "created_at": "2025-10-21T10:02:00", "updated_at": "2025-10-21T10:02:00"},
    {"id": 4, "name": "测试店铺D", "description": "测试店铺D的描述", "status": "active", "created_at": "2025-10-21T10:03:00", "updated_at": "2025-10-21T10:03:00"},
]


@api_bp.get("/shops")
def list_shops():
    """获取店铺列表 - 简化版"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")
    search = request.args.get("search", "").strip()

    all_shops = MOCK_SHOPS.copy()
    
    # 状态过滤
    if status:
        all_shops = [shop for shop in all_shops if shop["status"] == status]
    
    # 搜索过滤
    if search:
        all_shops = [shop for shop in all_shops if search.lower() in shop["name"].lower() or search.lower() in shop["description"].lower()]

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_shops = all_shops[start:end]

    return jsonify({
        "shops": paginated_shops,
        "total": len(all_shops),
        "page": page,
        "per_page": per_page,
        "pages": (len(all_shops) + per_page - 1) // per_page,
    })


@api_bp.post("/shops")
def create_shop():
    """创建店铺 - 简化版"""
    data = request.get_json(force=True) or {}
    
    required_fields = ["name"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field}_required"}), 400
    
    if any(shop["name"] == data["name"] for shop in MOCK_SHOPS):
        return jsonify({"error": "shop_name_exists"}), 400
    
    new_id = max(shop["id"] for shop in MOCK_SHOPS) + 1 if MOCK_SHOPS else 1
    new_shop = {
        "id": new_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "status": data.get("status", "active"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    MOCK_SHOPS.append(new_shop)
    
    return jsonify({
        "id": new_shop["id"],
        "message": "店铺创建成功"
    }), 201


@api_bp.get("/shops/<int:shop_id>")
def get_shop(shop_id):
    """获取单个店铺 - 简化版"""
    shop = next((s for s in MOCK_SHOPS if s["id"] == shop_id), None)
    if not shop:
        return jsonify({"error": "shop_not_found"}), 404
    return jsonify(shop)


@api_bp.put("/shops/<int:shop_id>")
def update_shop(shop_id: int):
    """更新店铺信息 - 简化版"""
    data = request.get_json(force=True) or {}
    shop_index = None
    for i, shop in enumerate(MOCK_SHOPS):
        if shop["id"] == shop_id:
            shop_index = i
            break
    
    if shop_index is None:
        return jsonify({"error": "shop_not_found"}), 404
    
    if "name" in data:
        MOCK_SHOPS[shop_index]["name"] = data["name"]
    if "description" in data:
        MOCK_SHOPS[shop_index]["description"] = data["description"]
    if "status" in data:
        MOCK_SHOPS[shop_index]["status"] = data["status"]
    
    MOCK_SHOPS[shop_index]["updated_at"] = datetime.now().isoformat()
    
    return jsonify({
        "message": "店铺更新成功",
        "shop": MOCK_SHOPS[shop_index]
    })


@api_bp.delete("/shops/<int:shop_id>")
def delete_shop(shop_id):
    """删除店铺 - 简化版"""
    global MOCK_SHOPS
    initial_len = len(MOCK_SHOPS)
    MOCK_SHOPS = [shop for shop in MOCK_SHOPS if shop["id"] != shop_id]
    if len(MOCK_SHOPS) == initial_len:
        return jsonify({"error": "shop_not_found"}), 404
    return jsonify({"message": "店铺删除成功"})
