"""
知识库向量检索（可选依赖降级）

优先使用 sentence-transformers 生成句向量；未安装则降级为关键词Jaccard相似度。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import math

try:  # 可选依赖
    from sentence_transformers import SentenceTransformer  # type: ignore
    _encoder: Optional[SentenceTransformer] = None
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore
    _encoder = None


@dataclass
class ScoredDoc:
    kb_item_id: int
    answer: str
    score: float


def _ensure_encoder(model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
    global _encoder
    if SentenceTransformer is None:
        return None
    if _encoder is None:
        _encoder = SentenceTransformer(model_name)
    return _encoder


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _token_set(s: str) -> set:
    return set([t for t in s.lower().replace('\n', ' ').split() if t])


def jaccard(a: str, b: str) -> float:
    sa, sb = _token_set(a), _token_set(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union


def embed(texts: List[str]) -> Optional[List[List[float]]]:
    encoder = _ensure_encoder()
    if encoder is None:
        return None
    vecs = encoder.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vecs]


def search_in_memory(query: str, corpus: List[Tuple[int, str, Optional[List[float]]]], top_k: int = 3) -> List[ScoredDoc]:
    """内存检索：若向量可用优先余弦，否则Jaccard。

    corpus: 列表 (kb_item_id, text, vector or None)
    """
    # 优先使用向量
    q_vecs = embed([query])
    results: List[ScoredDoc] = []
    if q_vecs is not None:
        qv = q_vecs[0]
        for kb_id, text, vec in corpus:
            if vec is None:
                # 回退到 Jaccard
                score = jaccard(query, text)
            else:
                score = _cosine(qv, vec)
            results.append(ScoredDoc(kb_item_id=kb_id, answer=text, score=float(score)))
    else:
        for kb_id, text, _ in corpus:
            score = jaccard(query, text)
            results.append(ScoredDoc(kb_item_id=kb_id, answer=text, score=float(score)))

    results.sort(key=lambda x: x.score, reverse=True)
    return results[: max(1, top_k)]


