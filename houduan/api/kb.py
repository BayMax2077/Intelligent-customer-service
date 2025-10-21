from __future__ import annotations

import json
import csv
import io
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from io import BytesIO

from flask import request, jsonify, send_file
from flask_login import login_required

from . import api_bp
from ..app import db
from ..models import KnowledgeBaseItem, KnowledgeVector, Shop, ImportTask
from ..utils.security import require_roles
from ..services.vector_search import search_in_memory, embed


@api_bp.get("/kb")
@login_required
def list_kb_items():
    """获取知识库条目列表"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        shop_id = request.args.get("shop_id", type=int)
        category = request.args.get("category")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            query = session.query(KnowledgeBaseItem)
            if shop_id:
                query = query.filter(KnowledgeBaseItem.shop_id == shop_id)
            if category:
                query = query.filter(KnowledgeBaseItem.category == category)
            
            # 手动实现分页
            total = query.count()
            items = query.order_by(KnowledgeBaseItem.id.asc()).offset((page - 1) * per_page).limit(per_page).all()
            pages = (total + per_page - 1) // per_page
            
            return jsonify({
                "items": [
                    {
                        "id": item.id,
                        "shop_id": item.shop_id,
                        "question": item.question,
                        "answer": item.answer,
                        "category": item.category,
                        "keywords": item.keywords,
                        "created_at": item.created_at.isoformat() if item.created_at else None,
                        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                    }
                    for item in items
                ],
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            })
        finally:
            session.close()
    except Exception as e:
        print(f"Error in list_kb_items: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/kb")
@login_required
@require_roles("superadmin", "admin")
def create_kb_item():
    """创建知识库条目"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        
        # 验证必填字段
        required_fields = ["question", "answer"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field}_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 创建知识库条目
            item = KnowledgeBaseItem(
                shop_id=data.get("shop_id"),
                question=data.get("question"),
                answer=data.get("answer"),
                category=data.get("category", ""),
                keywords=data.get("keywords", ""),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(item)
            session.commit()
            
            return jsonify({"ok": True, "id": item.id}), 201
        finally:
            session.close()
    except Exception as e:
        print(f"Error creating kb item: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api_bp.put("/kb/<int:item_id>")
@login_required
@require_roles("superadmin", "admin")
def update_kb_item(item_id: int):
    """更新知识库条目"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        data = request.get_json(force=True) or {}
        
        # 验证必填字段
        required_fields = ["question", "answer"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field}_required"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 查找条目
            item = session.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.id == item_id).first()
            if not item:
                return jsonify({"error": "item_not_found"}), 404
            
            # 更新条目
            item.shop_id = data.get("shop_id")
            item.question = data.get("question")
            item.answer = data.get("answer")
            item.category = data.get("category", "")
            item.keywords = data.get("keywords", "")
            item.updated_at = datetime.now()
            
            session.commit()
            
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error updating kb item: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api_bp.delete("/kb/<int:item_id>")
@login_required
@require_roles("superadmin", "admin")
def delete_kb_item(item_id: int):
    """删除知识库条目"""
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
            # 查找条目
            item = session.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.id == item_id).first()
            if not item:
                return jsonify({"error": "item_not_found"}), 404
            
            # 删除条目
            session.delete(item)
            session.commit()
            
            return jsonify({"ok": True})
        finally:
            session.close()
    except Exception as e:
        print(f"Error deleting kb item: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api_bp.get("/kb/categories")
@login_required
def list_categories():
    """获取分类列表"""
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
            # 获取所有分类
            categories = session.query(KnowledgeBaseItem.category).distinct().all()
            category_list = [cat[0] for cat in categories if cat[0]]
            
            return jsonify(category_list)
        finally:
            session.close()
    except Exception as e:
        print(f"Error listing categories: {e}")
        return jsonify({"error": "database_error", "detail": str(e)}), 500


@api_bp.post("/kb/import")
@login_required
@require_roles("superadmin", "admin")
def import_kb_data():
    """批量导入知识库数据 - 增强版错误处理"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({"error": "no_file", "message": "请选择要导入的文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "no_file_selected", "message": "请选择要导入的文件"}), 400
        
        # 验证文件类型
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({"error": "invalid_file_type", "message": "只支持Excel文件格式(.xlsx, .xls)"}), 400
        
        # 读取Excel文件
        try:
            df = pd.read_excel(file)
            print(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            return jsonify({
                "error": "invalid_file", 
                "message": f"Excel文件读取失败: {str(e)}",
                "detail": "请检查文件格式是否正确，或文件是否损坏"
            }), 400
        
        # 检查必要的列
        required_columns = ['问题', '答案']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                "error": "missing_columns", 
                "message": f"Excel文件缺少必要的列: {', '.join(missing_columns)}",
                "detail": f"当前文件包含的列: {list(df.columns)}",
                "required_columns": required_columns,
                "actual_columns": list(df.columns)
            }), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 创建导入任务记录
            import_task = ImportTask(
                task_name=f"知识库导入_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                file_name=file.filename,
                file_size=len(file.read()),
                status='processing',
                progress=0,
                total_rows=len(df),
                processed_rows=0,
                success_count=0,
                error_count=0,
                started_at=datetime.now(),
                config_json=json.dumps({
                    "skip_duplicates": True,
                    "auto_create_shops": True,
                    "validate_data": True,
                    "generate_vectors": True
                })
            )
            file.seek(0)  # 重置文件指针
            
            session.add(import_task)
            session.commit()
            task_id = import_task.id
            
            # 处理数据
            success_count = 0
            error_count = 0
            errors = []
            warnings = []
            
            print(f"开始处理{len(df)}行数据，任务ID: {task_id}")
            
            for index, row in df.iterrows():
                row_number = index + 2  # Excel行号从2开始
                
                try:
                    # 检查数据有效性
                    question = str(row['问题']).strip() if pd.notna(row['问题']) else ""
                    answer = str(row['答案']).strip() if pd.notna(row['答案']) else ""
                    
                    # 验证必填字段
                    if not question:
                        error_msg = f"第{row_number}行: 问题字段不能为空"
                        errors.append(error_msg)
                        error_count += 1
                        continue
                        
                    if not answer:
                        error_msg = f"第{row_number}行: 答案字段不能为空"
                        errors.append(error_msg)
                        error_count += 1
                        continue
                    
                    # 检查是否是数字类型的问题和答案
                    if question.isdigit():
                        error_msg = f"第{row_number}行: 问题不能为纯数字，请填写实际的问答内容"
                        errors.append(error_msg)
                        error_count += 1
                        continue
                        
                    if answer.isdigit():
                        error_msg = f"第{row_number}行: 答案不能为纯数字，请填写实际的问答内容"
                        errors.append(error_msg)
                        error_count += 1
                        continue
                    
                    # 处理条目归属
                    shop_id = None
                    shop_name = "全局知识库"
                    
                    if '条目归属' in df.columns and pd.notna(row['条目归属']):
                        attribution = str(row['条目归属']).strip()
                        if attribution and attribution not in ["", "全局", "全局知识库"]:
                            # 根据店铺名称查找店铺ID
                            shop = session.query(Shop).filter_by(name=attribution).first()
                            if shop:
                                shop_id = shop.id
                                shop_name = shop.name
                            else:
                                error_msg = f"第{row_number}行: 店铺 '{attribution}' 不存在，请先在店铺配置中创建该店铺"
                                errors.append(error_msg)
                                error_count += 1
                                continue
                    
                    # 创建知识库条目
                    item = KnowledgeBaseItem(
                        shop_id=shop_id,
                        question=question,
                        answer=answer,
                        category=str(row.get('分类', '')).strip() if pd.notna(row.get('分类')) else "",
                        keywords=str(row.get('关键词', '')).strip() if pd.notna(row.get('关键词')) else "",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(item)
                    session.flush()  # 获取ID但不提交
                    success_count += 1
                    
                    print(f"[成功] 第{row_number}行: 成功创建 - {shop_name}")
                    
                except Exception as e:
                    error_msg = f"第{row_number}行: 处理失败 - {str(e)}"
                    errors.append(error_msg)
                    error_count += 1
                    print(f"[错误] {error_msg}")
                    continue
            
            # 提交所有成功的数据
            session.commit()
            print(f"数据库事务已提交，成功导入{success_count}条数据")
            
            # 更新导入任务状态
            import_task.status = 'completed'
            import_task.progress = 100
            import_task.processed_rows = len(df)
            import_task.success_count = success_count
            import_task.error_count = error_count
            import_task.completed_at = datetime.now()
            import_task.results_json = json.dumps({
                "success_count": success_count,
                "error_count": error_count,
                "total_rows": len(df),
                "success_rate": round((success_count / len(df)) * 100, 2) if len(df) > 0 else 0,
                "errors": errors[:20] if errors else [],
                "processing_time": 0  # 可以添加实际处理时间
            })
            session.commit()
            
            # 构建详细的结果
            result = {
                "ok": True,
                "message": f"导入完成！成功: {success_count}条, 失败: {error_count}条",
                "success_count": success_count,
                "error_count": error_count,
                "total_rows": len(df),
                "success_rate": round((success_count / len(df)) * 100, 2) if len(df) > 0 else 0,
                "task_id": task_id
            }
            
            # 如果有错误，添加错误详情
            if errors:
                result["errors"] = errors[:20]  # 只返回前20个错误
                result["error_summary"] = f"共发现{len(errors)}个错误，已显示前20个"
            
            # 如果有警告，添加警告详情
            if warnings:
                result["warnings"] = warnings
            
            return jsonify(result)
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"导入过程中发生严重错误: {e}")
        
        # 如果有任务记录，更新为失败状态
        if 'import_task' in locals():
            try:
                import_task.status = 'failed'
                import_task.error_message = str(e)
                import_task.completed_at = datetime.now()
                session.commit()
            except:
                pass
        
        return jsonify({
            "error": "import_failed", 
            "message": f"导入失败: {str(e)}",
            "detail": "请检查文件格式和内容是否正确，或联系技术支持"
        }), 500


@api_bp.get("/kb/export")
@login_required
def export_kb_data():
    """导出知识库数据"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        shop_id = request.args.get("shop_id", type=int)
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 查询数据
            query = session.query(KnowledgeBaseItem)
            if shop_id:
                query = query.filter(KnowledgeBaseItem.shop_id == shop_id)
            
            items = query.all()
            
            # 创建Excel文件
            data = []
            for item in items:
                data.append({
                    'ID': item.id,
                    '条目归属': item.shop_id or '全局知识库',
                    '问题': item.question,
                    '答案': item.answer,
                    '分类': item.category,
                    '关键词': item.keywords,
                    '创建时间': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
                    '更新时间': item.updated_at.strftime('%Y-%m-%d %H:%M:%S') if item.updated_at else ''
                })
            
            df = pd.DataFrame(data)
            
            # 创建Excel文件
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='知识库数据')
            
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'知识库数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"Error exporting kb data: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api_bp.get("/kb/template")
@login_required
def download_template():
    """下载Excel模板"""
    try:
        # 创建模板数据
        template_data = [
            {
                'ID': '',
                '条目归属': '全局知识库',
                '问题': '如何联系客服？',
                '答案': '您可以通过以下方式联系我们的客服：1. 在线客服（工作时间9:00-18:00）2. 客服电话：400-123-4567 3. 邮箱：service@example.com',
                '分类': '客服咨询',
                '关键词': '联系,客服,电话,邮箱',
                '创建时间': '',
                '更新时间': ''
            },
            {
                'ID': '',
                '条目归属': '全局知识库',
                '问题': '什么时候发货？',
                '答案': '一般情况下，我们会在您下单后1-2个工作日内发货。具体发货时间可能会因商品库存、物流情况等因素有所调整。',
                '分类': '物流配送',
                '关键词': '发货,物流,配送,时间',
                '创建时间': '',
                '更新时间': ''
            },
            {
                'ID': '',
                '条目归属': '全局知识库',
                '问题': '支持哪些支付方式？',
                '答案': '我们支持多种支付方式：1. 支付宝 2. 微信支付 3. 银行卡支付 4. 信用卡支付。所有支付方式都经过安全加密处理，保障您的资金安全。',
                '分类': '支付相关',
                '关键词': '支付,支付宝,微信,银行卡,信用卡',
                '创建时间': '',
                '更新时间': ''
            }
        ]
        
        # 创建DataFrame
        df = pd.DataFrame(template_data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='知识库模板')
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='知识库导入模板.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"Error downloading template: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@api_bp.post("/kb/batch-delete")
@login_required
@require_roles("superadmin", "admin")
def batch_delete_kb_items():
    """批量删除知识库条目"""
    try:
        from flask import current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 使用JSON数据方式
        data = request.get_json(force=True) or {}
        item_ids = data.get("item_ids", [])
        confirm = data.get("confirm", False)
        
        if not item_ids:
            return jsonify({"error": "no_items_selected", "message": "没有选择要删除的条目"}), 400
        
        if not confirm:
            return jsonify({"error": "confirmation_required", "message": "需要确认删除操作"}), 400
        
        if not isinstance(item_ids, list) or len(item_ids) == 0:
            return jsonify({"error": "invalid_item_ids", "message": "无效的条目ID列表"}), 400
        
        # 验证条目ID都是整数
        try:
            item_ids = [int(id) for id in item_ids]
        except (ValueError, TypeError):
            return jsonify({"error": "invalid_item_ids", "message": "条目ID必须是整数"}), 400
        
        # 直接创建数据库连接
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 验证条目是否存在
            existing_items = session.query(KnowledgeBaseItem).filter(
                KnowledgeBaseItem.id.in_(item_ids)
            ).all()
            
            existing_ids = [item.id for item in existing_items]
            missing_ids = [id for id in item_ids if id not in existing_ids]
            
            if missing_ids:
                return jsonify({
                    "error": "items_not_found", 
                    "message": f"以下条目不存在: {missing_ids}",
                    "missing_ids": missing_ids
                }), 404
            
            # 开始事务
            deleted_count = 0
            failed_count = 0
            errors = []
            
            for item in existing_items:
                try:
                    # 删除相关的向量数据
                    session.query(KnowledgeVector).filter(
                        KnowledgeVector.kb_item_id == item.id
                    ).delete()
                    
                    # 删除知识库条目
                    session.delete(item)
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"Error deleting item {item.id}: {e}")
                    failed_count += 1
                    errors.append(f"删除条目 {item.id} 失败: {str(e)}")
            
            # 提交事务
            session.commit()
            
            return jsonify({
                "ok": True,
                "message": f"批量删除完成，成功删除 {deleted_count} 条，失败 {failed_count} 条",
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "errors": errors
            })
            
        except Exception as e:
            session.rollback()
            print(f"Error in batch delete transaction: {e}")
            return jsonify({
                "error": "batch_delete_failed", 
                "message": f"批量删除失败: {str(e)}"
            }), 500
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"Error in batch_delete_kb_items: {e}")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


