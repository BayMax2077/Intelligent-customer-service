"""
消息处理引擎（骨架）

流程:
1) 输入消息文本 -> 知识库匹配
2) 命中高置信度: 直接使用知识库答案, 标记可自动发送
3) 中低置信度: 组合上下文 -> 走 AI 生成, 进入审核
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from ..app import db
from ..models import Message, AIReply, AuditQueueItem, StatisticsDaily
from .knowledge_base import match_from_knowledge_base
from .ai_adapter import generate_reply
from ..models import Shop
from datetime import datetime, date


@dataclass
class ProcessResult:
    reply: str
    source: str  # kb/ai
    auto_send: bool
    confidence: float


def update_daily_statistics(shop_id: int, source: str, auto_send: bool):
    """更新日统计数据"""
    try:
        today = date.today()
        stats = StatisticsDaily.query.filter_by(date=today).first()
        
        if not stats:
            stats = StatisticsDaily(date=today)
            db.session.add(stats)
        
        # 这里可以添加更多统计指标
        # 由于当前模型设计较简单，这里先记录基本统计
        # 实际项目中可以扩展为更详细的统计表
        
        db.session.commit()
    except Exception:
        # 统计失败不影响主流程
        pass


def process_message(message: Message) -> ProcessResult:
    # 检查黑白名单
    shop = db.session.get(Shop, message.shop_id)
    if shop and shop.config_json:
        import json as _json
        try:
            cfg = _json.loads(shop.config_json)
            customer_id = message.customer_id
            
            # 检查黑名单
            blacklist = cfg.get("blacklist", [])
            if blacklist and customer_id in blacklist:
                # 黑名单用户，直接拒绝
                ai = AIReply(message_id=message.id, model="blacklist", reply="抱歉，您已被加入黑名单，无法获得自动回复服务。", confidence=1.0, review_status="auto")
                db.session.add(ai)
                message.status = "answered"
                db.session.commit()
                return ProcessResult(reply="抱歉，您已被加入黑名单，无法获得自动回复服务。", source="blacklist", auto_send=True, confidence=1.0)
            
            # 检查白名单（如果设置了白名单，只有白名单用户才能获得服务）
            whitelist = cfg.get("whitelist", [])
            if whitelist and customer_id not in whitelist:
                # 非白名单用户，直接拒绝
                ai = AIReply(message_id=message.id, model="whitelist", reply="抱歉，您不在服务白名单中，无法获得自动回复服务。", confidence=1.0, review_status="auto")
                db.session.add(ai)
                message.status = "answered"
                db.session.commit()
                return ProcessResult(reply="抱歉，您不在服务白名单中，无法获得自动回复服务。", source="whitelist", auto_send=True, confidence=1.0)
                
        except Exception:
            pass  # 配置解析失败，继续正常流程
    
    # 检查营业时间
    if shop and shop.config_json:
        try:
            cfg = _json.loads(shop.config_json)
            business_hours = cfg.get("business_hours")
            if business_hours:
                from datetime import datetime
                now = datetime.now().time()
                start_time = datetime.strptime(business_hours.get("start", "09:00"), "%H:%M").time()
                end_time = datetime.strptime(business_hours.get("end", "22:00"), "%H:%M").time()
                
                if not (start_time <= now <= end_time):
                    # 非营业时间
                    ai = AIReply(message_id=message.id, model="business_hours", reply="您好，当前为非营业时间，我们会在营业时间内尽快回复您。营业时间：{} - {}".format(business_hours.get("start", "09:00"), business_hours.get("end", "22:00")), confidence=1.0, review_status="auto")
                    db.session.add(ai)
                    message.status = "answered"
                    db.session.commit()
                    return ProcessResult(reply="您好，当前为非营业时间，我们会在营业时间内尽快回复您。", source="business_hours", auto_send=True, confidence=1.0)
        except Exception:
            pass  # 营业时间解析失败，继续正常流程
    
    # 正常的知识库和AI处理流程
    kb = match_from_knowledge_base(message.shop_id, message.content)
    if kb and kb.confidence >= 0.9:
        # 直接使用知识库答案
        ai = AIReply(message_id=message.id, model="kb", reply=kb.answer, confidence=kb.confidence, review_status="auto")
        db.session.add(ai)
        message.status = "answered"
        db.session.commit()
        return ProcessResult(reply=kb.answer, source="kb", auto_send=True, confidence=kb.confidence)

    # 需要 AI 辅助
    context = kb.answer if kb else None
    # 读取店铺AI模型配置
    model = "stub"
    if shop and shop.config_json:
        try:
            cfg = _json.loads(shop.config_json)
            model = cfg.get("ai_model", "stub")
        except Exception:
            pass
    
    ai_text = generate_reply(prompt=message.content, context=context, model=model)
    ai = AIReply(message_id=message.id, model=model, reply=ai_text, confidence=(kb.confidence if kb else 0.6), review_status="pending")
    db.session.add(ai)
    db.session.add(AuditQueueItem(message_id=message.id, status="pending"))
    message.status = "review"
    db.session.commit()
    
    # 更新统计数据
    update_daily_statistics(message.shop_id, "ai", False)
    
    return ProcessResult(reply=ai_text, source="ai", auto_send=False, confidence=kb.confidence if kb else 0.6)


