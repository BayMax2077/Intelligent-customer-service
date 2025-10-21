"""
知识库匹配服务

提供:
- 从数据库加载知识库条目
- 向量检索优先，关键词匹配回退
- 支持多店铺独立知识库
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple

from ..app import db
from ..models import KnowledgeBaseItem
from .vector_search import search_in_memory, embed


@dataclass
class KBMatchResult:
    answer: str
    confidence: float  # 0~1
    kb_item_id: Optional[int] = None


def match_from_knowledge_base(shop_id: int, text: str) -> Optional[KBMatchResult]:
    """从数据库加载知识库条目进行匹配，优先向量检索，回退到关键词匹配。"""
    q = (text or "").lower().strip()
    if not q:
        return None
    
    # 从数据库加载知识库条目
    kb_query = KnowledgeBaseItem.query
    if shop_id:
        # 优先匹配店铺专用知识库，然后匹配全局知识库
        kb_query = kb_query.filter(
            (KnowledgeBaseItem.shop_id == shop_id) | (KnowledgeBaseItem.shop_id.is_(None))
        )
    else:
        # 仅匹配全局知识库
        kb_query = kb_query.filter(KnowledgeBaseItem.shop_id.is_(None))
    
    items = kb_query.all()
    if not items:
        return None
    
    # 构建语料库进行向量检索
    corpus: List[Tuple[int, str, Optional[List[float]]]] = [
        (item.id, item.question + " " + item.answer, None)
        for item in items
    ]
    
    # 向量检索
    hits = search_in_memory(q, corpus, top_k=1)
    if hits and hits[0].score >= 0.6:
        best = hits[0]
        return KBMatchResult(answer=best.answer, confidence=float(best.score), kb_item_id=best.kb_item_id)
    
    # 关键词匹配回退
    for item in items:
        # 检查问题中的关键词
        question_keywords = (item.keywords or "").lower().split(",")
        question_keywords = [kw.strip() for kw in question_keywords if kw.strip()]
        
        # 检查问题文本中的关键词
        question_text = item.question.lower()
        
        # 关键词匹配
        if any(kw in q for kw in question_keywords):
            return KBMatchResult(
                answer=item.answer, 
                confidence=0.85, 
                kb_item_id=item.id
            )
        
        # 问题文本匹配
        if any(word in q for word in question_text.split() if len(word) > 2):
            return KBMatchResult(
                answer=item.answer, 
                confidence=0.75, 
                kb_item_id=item.id
            )
    
    # 硬编码关键词匹配（兜底）
    if any(k in q for k in ["退款", "退货", "售后", "refund"]):
        return KBMatchResult(answer="您好，售后/退款请提供订单号与问题描述，我们为您处理。", confidence=0.92)
    if any(k in q for k in ["发票", "invoice"]):
        return KBMatchResult(answer="电子发票可在订单详情下载，如需纸质请留言收件信息。", confidence=0.88)
    
    return None


