"""
数据模型集中导出

包含: 用户、店铺、消息、知识库、向量索引、AI 回复、模板、审核队列、统计
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..app import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="agent")  # superadmin/admin/agent
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=True)


class Shop(db.Model, TimestampMixin):
    __tablename__ = "shops"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    qianniu_title = db.Column(db.String(256), nullable=True)  # 千牛窗口标题标识
    config_json = db.Column(db.Text, nullable=True)


class Message(db.Model, TimestampMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    customer_id = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(32), nullable=False, default="qianniu")
    status = db.Column(db.String(32), nullable=False, default="new")  # new/answered/queued/review
    handled_by = db.Column(db.String(64), nullable=True)


class KnowledgeBaseItem(db.Model, TimestampMixin):
    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=True)  # 为空表示全局
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64), nullable=True)
    keywords = db.Column(db.String(512), nullable=True)  # 逗号分隔关键词


class KnowledgeVector(db.Model, TimestampMixin):
    __tablename__ = "knowledge_vectors"

    id = db.Column(db.Integer, primary_key=True)
    kb_item_id = db.Column(db.Integer, db.ForeignKey("knowledge_base.id"), nullable=False)
    vector = db.Column(db.LargeBinary, nullable=False)  # 存储向量 bytes（FAISS/Milvus 外部索引可选）
    dim = db.Column(db.Integer, nullable=False)


class AIReply(db.Model, TimestampMixin):
    __tablename__ = "ai_replies"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("messages.id"), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    reply = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    review_status = db.Column(db.String(32), nullable=False, default="auto")  # auto/pending/approved/rejected


class ReplyTemplate(db.Model, TimestampMixin):
    __tablename__ = "reply_templates"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)


class AuditQueueItem(db.Model, TimestampMixin):
    __tablename__ = "audit_queue"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("messages.id"), nullable=False)
    assigned_to = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), nullable=False, default="pending")  # pending/approved/rejected
    note = db.Column(db.Text, nullable=True)


class StatisticsDaily(db.Model, TimestampMixin):
    __tablename__ = "statistics_daily"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    kb_hit_rate = db.Column(db.Float, nullable=True)
    ai_accuracy = db.Column(db.Float, nullable=True)


class ImportTask(db.Model, TimestampMixin):
    __tablename__ = "import_tasks"

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pending")  # pending/processing/completed/failed/cancelled
    progress = db.Column(db.Integer, nullable=False, default=0)
    total_rows = db.Column(db.Integer, nullable=True)
    processed_rows = db.Column(db.Integer, nullable=False, default=0)
    success_count = db.Column(db.Integer, nullable=False, default=0)
    error_count = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    config_json = db.Column(db.Text, nullable=True)  # 导入配置（后端写死）
    results_json = db.Column(db.Text, nullable=True)  # 处理结果详情


class ImportTaskLog(db.Model, TimestampMixin):
    __tablename__ = "import_task_logs"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("import_tasks.id"), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # info/warning/error
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


