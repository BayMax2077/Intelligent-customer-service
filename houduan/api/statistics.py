from __future__ import annotations

from datetime import datetime, date, timedelta
from flask import request, jsonify
from flask_login import login_required

from . import api_bp


@api_bp.get("/statistics/daily")
@login_required
def get_daily_statistics():
    """获取日统计数据 - 简化版"""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    # 默认查询最近30天
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    try:
        start_dt = datetime.fromisoformat(start_date).date()
        end_dt = datetime.fromisoformat(end_date).date()
    except ValueError:
        return jsonify({"error": "invalid_date_format"}), 400
    
    # 生成模拟数据
    daily_data = []
    current_date = start_dt
    while current_date <= end_dt:
        # 模拟数据：每天随机生成一些消息
        import random
        daily_messages = random.randint(0, 20)
        daily_kb_hits = int(daily_messages * 0.75)
        daily_ai_suggestions = int(daily_messages * 0.6)
        daily_auto_sent = int(daily_messages * 0.4)
        daily_manual_reviewed = int(daily_messages * 0.2)
        
        daily_data.append({
            "date": current_date.isoformat(),
            "total_messages": daily_messages,
            "kb_hits": daily_kb_hits,
            "ai_suggestions": daily_ai_suggestions,
            "auto_sent": daily_auto_sent,
            "manual_reviewed": daily_manual_reviewed,
            "kb_hit_rate": 0.75 if daily_messages > 0 else 0.0,
            "auto_send_rate": 0.4 if daily_messages > 0 else 0.0
        })
        current_date += timedelta(days=1)
    
    # 计算汇总数据
    total_messages = sum(data["total_messages"] for data in daily_data)
    total_kb_hits = sum(data["kb_hits"] for data in daily_data)
    total_ai_suggestions = sum(data["ai_suggestions"] for data in daily_data)
    total_auto_sent = sum(data["auto_sent"] for data in daily_data)
    total_manual_reviewed = sum(data["manual_reviewed"] for data in daily_data)
    
    avg_kb_hit_rate = 0.75 if total_messages > 0 else 0.0
    avg_auto_send_rate = 0.4 if total_messages > 0 else 0.0
    
    return jsonify({
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "daily_data": daily_data,
        "summary": {
            "total_messages": total_messages,
            "total_kb_hits": total_kb_hits,
            "total_ai_suggestions": total_ai_suggestions,
            "total_auto_sent": total_auto_sent,
            "total_manual_reviewed": total_manual_reviewed,
            "avg_kb_hit_rate": avg_kb_hit_rate,
            "avg_auto_send_rate": avg_auto_send_rate
        }
    })


@api_bp.get("/statistics/knowledge_base")
@login_required
def get_kb_statistics():
    """获取知识库统计 - 简化版"""
    # 模拟知识库数据
    return jsonify({
        "total_items": 40,
        "by_category": [
            {"category": "产品咨询", "count": 15},
            {"category": "技术支持", "count": 12},
            {"category": "售后服务", "count": 8},
            {"category": "价格咨询", "count": 3},
            {"category": "物流查询", "count": 2}
        ],
        "by_shop": [
            {"shop_id": "1", "count": 20},
            {"shop_id": "2", "count": 15},
            {"shop_id": "全局", "count": 5}
        ]
    })


@api_bp.get("/statistics/performance")
@login_required
def get_performance_statistics():
    """获取性能统计 - 简化版"""
    # 模拟性能数据
    return jsonify({
        "period": {
            "start_date": (date.today() - timedelta(days=7)).isoformat(),
            "end_date": date.today().isoformat()
        },
        "total_messages": 150,
        "total_ai_replies": 120,
        "model_performance": {
            "stub": {"count": 80, "avg_confidence": 0.85},
            "qwen": {"count": 60, "avg_confidence": 0.82},
            "ernie": {"count": 40, "avg_confidence": 0.88}
        },
        "response_times": {
            "avg_processing_time": "1.2s",
            "fastest_response": "0.8s",
            "slowest_response": "2.1s"
        }
    })
