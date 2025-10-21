"""
导入任务管理API

提供导入任务的创建、监控、历史查询等功能
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from flask import request, jsonify, current_app
from flask_login import login_required

from ..app import db
from ..models import ImportTask, ImportTaskLog
from ..utils.security import require_roles
from . import api_bp


# 后端写死的导入配置
IMPORT_CONFIG = {
    "skip_duplicates": True,      # 跳过重复数据
    "auto_create_shops": True,    # 自动创建店铺
    "validate_data": True,        # 数据验证
    "generate_vectors": True,     # 生成向量
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_extensions": [".xlsx", ".xls"],
    "required_columns": ["条目归属", "问题", "答案"],
    "optional_columns": ["分类", "关键词"],
    "business_rules": {
        "max_question_length": 1000,
        "max_answer_length": 5000,
        "required_shop_exists": True
    }
}


@api_bp.get("/import/tasks")
@login_required
def list_import_tasks():
    """获取导入任务列表"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            status = request.args.get('status', '')
            search = request.args.get('search', '')
            
            # 构建查询
            query = session.query(ImportTask)
            
            # 状态筛选
            if status:
                query = query.filter(ImportTask.status == status)
            
            # 搜索筛选
            if search:
                query = query.filter(
                    ImportTask.task_name.contains(search) |
                    ImportTask.file_name.contains(search)
                )
            
            # 排序和分页
            query = query.order_by(ImportTask.created_at.desc())
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建结果
            result = []
            for task in items:
                result.append({
                    "id": task.id,
                    "task_name": task.task_name,
                    "file_name": task.file_name,
                    "file_size": task.file_size,
                    "status": task.status,
                    "progress": task.progress,
                    "total_rows": task.total_rows,
                    "processed_rows": task.processed_rows,
                    "success_count": task.success_count,
                    "error_count": task.error_count,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error_message": task.error_message
                })
            
            return jsonify({
                "items": result,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in list_import_tasks: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.get("/import/tasks/<int:task_id>")
@login_required
def get_import_task(task_id: int):
    """获取导入任务详情"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            task = session.query(ImportTask).filter(ImportTask.id == task_id).first()
            if not task:
                return jsonify({"error": "task_not_found"}), 404
            
            # 解析配置和结果
            config = {}
            if task.config_json:
                try:
                    config = json.loads(task.config_json)
                except Exception:
                    config = {}
            
            results = {}
            if task.results_json:
                try:
                    results = json.loads(task.results_json)
                except Exception:
                    results = {}
            
            return jsonify({
                "id": task.id,
                "task_name": task.task_name,
                "file_name": task.file_name,
                "file_size": task.file_size,
                "status": task.status,
                "progress": task.progress,
                "total_rows": task.total_rows,
                "processed_rows": task.processed_rows,
                "success_count": task.success_count,
                "error_count": task.error_count,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message,
                "config": config,
                "results": results
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in get_import_task: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.get("/import/tasks/<int:task_id>/logs")
@login_required
def get_import_task_logs(task_id: int):
    """获取导入任务日志"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 100))
            level = request.args.get('level', '')
            
            # 构建查询
            query = session.query(ImportTaskLog).filter(ImportTaskLog.task_id == task_id)
            
            # 级别筛选
            if level:
                query = query.filter(ImportTaskLog.level == level)
            
            # 排序和分页
            query = query.order_by(ImportTaskLog.timestamp.desc())
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建结果
            result = []
            for log in items:
                result.append({
                    "id": log.id,
                    "level": log.level,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                })
            
            return jsonify({
                "items": result,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in get_import_task_logs: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/import/tasks/<int:task_id>/cancel")
@login_required
@require_roles("superadmin", "admin")
def cancel_import_task(task_id: int):
    """取消导入任务"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            task = session.query(ImportTask).filter(ImportTask.id == task_id).first()
            if not task:
                return jsonify({"error": "task_not_found"}), 404
            
            # 只有进行中的任务才能取消
            if task.status not in ["pending", "processing"]:
                return jsonify({"error": "task_not_cancellable"}), 400
            
            # 更新任务状态
            task.status = "cancelled"
            task.completed_at = datetime.utcnow()
            session.commit()
            
            # 添加日志
            log = ImportTaskLog(
                task_id=task_id,
                level="info",
                message="任务已被用户取消"
            )
            session.add(log)
            session.commit()
            
            return jsonify({"message": "任务已取消"})
        finally:
            session.close()
    except Exception as e:
        print(f"Error in cancel_import_task: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.get("/import/tasks/current")
@login_required
def get_current_import_task():
    """获取当前进行中的导入任务"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 查找进行中的任务
            task = session.query(ImportTask).filter(
                ImportTask.status.in_(["pending", "processing"])
            ).order_by(ImportTask.created_at.desc()).first()
            
            if not task:
                return jsonify({"task": None})
            
            return jsonify({
                "task": {
                    "id": task.id,
                    "task_name": task.task_name,
                    "file_name": task.file_name,
                    "status": task.status,
                    "progress": task.progress,
                    "total_rows": task.total_rows,
                    "processed_rows": task.processed_rows,
                    "success_count": task.success_count,
                    "error_count": task.error_count,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "started_at": task.started_at.isoformat() if task.started_at else None
                }
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in get_current_import_task: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.get("/import/config")
@login_required
def get_import_config():
    """获取导入配置（后端写死的配置）"""
    return jsonify(IMPORT_CONFIG)
