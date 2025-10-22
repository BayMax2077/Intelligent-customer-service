from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

# 延迟导入，避免SQLAlchemy连接问题
# from ..app import db
# from ..models import Shop, Message
from .qianniu_monitor import poll_and_capture, cleanup_caches
from .alert import check_system_health
from ..utils.context_manager import context_manager, safe_db_query, safe_db_commit


_scheduler: BackgroundScheduler | None = None


def start_scheduler(app):
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    sched = BackgroundScheduler()

    @sched.scheduled_job('interval', seconds=10, id='qianniu_poll')
    def job_poll():
        # 定期清理缓存
        cleanup_caches()
        
        # 保守处理：若数据库尚未初始化或绑定失败，不抛异常以免打断主请求流
        try:
            with context_manager.app_context(app):
                # 延迟导入，避免SQLAlchemy连接问题
                try:
                    from ..app import db
                    from ..models import Shop, Message
                except Exception as e:
                    logger.warning(f"Failed to import database models: {e}")
                    return
                
                # 使用安全的数据库查询
                shops = safe_db_query(lambda: Shop.query.all())
                if not shops:
                    return
                
                for i, s in enumerate(shops):
                    try:
                        import json as _json
                        cfg = _json.loads(s.config_json) if s.config_json else {}
                    except Exception:
                        cfg = {}
                    
                    # 多店铺轮询：每个店铺间隔2秒，避免窗口切换过快
                    if i > 0:
                        import time
                        time.sleep(2)
                    
                    # 检查店铺是否启用自动模式
                    if not cfg.get("auto_mode", False):
                        logger.info(f"Shop {s.id} auto mode disabled, skipping")
                        continue
                    
                    # 检查千牛窗口是否存在
                    if s.qianniu_title:
                        from .qianniu_monitor import list_windows_by_title
                        windows = list_windows_by_title(s.qianniu_title)
                        if not windows:
                            logger.info(f"No windows found for shop {s.id} with title '{s.qianniu_title}'")
                            continue
                    
                    score, text = poll_and_capture(cfg, s.id)
                    if text:
                        msg = Message(shop_id=s.id, customer_id='unknown', content=text, source='qianniu', status='new')
                        db.session.add(msg)
                        safe_db_commit(lambda: db.session.commit())
                        logger.info(f"Captured message for shop={s.id}, score={score:.3f}, len={len(text)}")
                    elif score >= cfg.get("unread_threshold", 0.02):
                        logger.info(f"Duplicate message detected for shop={s.id}, score={score:.3f}")
        except Exception as e:  # 避免 500 污染接口
            logger.warning(f"scheduler skipped due to init error: {e}")

    @sched.scheduled_job('interval', minutes=5, id='health_check')
    def job_health_check():
        """系统健康检查任务"""
        try:
            with context_manager.app_context(app):
                # 延迟导入，避免SQLAlchemy连接问题
                try:
                    check_system_health()
                except Exception as e:
                    logger.warning(f"health check failed: {e}")
        except Exception as e:
            logger.warning(f"health check failed: {e}")

    sched.start()
    _scheduler = sched
    return sched


