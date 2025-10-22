"""
淘宝千牛智能客服系统 - 后端入口

功能:
1) 初始化 Flask 应用、数据库、迁移、登录管理、跨域
2) 统一加载配置, 提供健康检查与基础路由

说明:
- 数据库默认使用 SQLite, 可通过环境变量 DATABASE_URL 切换到 MySQL 等
"""

from __future__ import annotations

import os
from datetime import datetime
from flask import Flask, jsonify, request, make_response, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from .config import Config
from .utils.db_manager import init_database_manager, db_manager

# 全局扩展实例(延迟绑定)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app() -> Flask:
    """创建并配置 Flask 应用实例。"""
    # 将前端构建产物作为静态目录托管，避免本地联调的跨域问题
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dist = os.path.normpath(os.path.join(base_dir, "..", "qianduan", "dist"))
    app = Flask(__name__, static_folder=static_dist, static_url_path="/")
    app.config["STATIC_DIST"] = static_dist
    app.config.from_object(Config())

    # 会话 Cookie 策略：确保跨端口(5174->5002)的 XHR 能携带会话
    # 本地开发为 HTTP，生产(HTTPS)需将 SECURE 设为 True
    is_https = False
    app.config["SESSION_COOKIE_NAME"] = "ics_session"
    # 开发(HTTP)下使用 Lax，生产(HTTPS)可配 None+Secure
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax" if not is_https else "None"
    app.config["SESSION_COOKIE_SECURE"] = bool(is_https)
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 初始化数据库管理器
    try:
        init_database_manager(app)
        print("数据库管理器初始化成功")
        
        # 启动数据库健康监控
        try:
            from .services.db_health import start_db_health_monitoring
            start_db_health_monitoring(app)
            print("数据库健康监控已启动")
        except Exception as e:
            print(f"数据库健康监控启动失败: {e}")
            
    except Exception as e:
        print(f"数据库管理器初始化失败: {e}")
        # 继续运行，使用简化版API
    # 开发联调需要携带 Cookie，不能使用 *。为了兼容局域网 IP 访问（如 192.168.x.x），
    # 这里放宽跨域来源：localhost/127.0.0.1 以及常见内网网段 192.168.*.* / 10.*.*.* / 172.16-31.*.*
    import re
    ports = list(range(5173, 5201))
    static_origins = [
        *(f"http://localhost:{p}" for p in ports),
        *(f"http://127.0.0.1:{p}" for p in ports),
    ]
    # 允许常见内网网段（带端口）
    lan_origin_pattern = re.compile(r"^https?://(?:(?:192\.168|10\.|172\.(?:1[6-9]|2[0-9]|3[0-1]))\.[0-9]{1,3}\.[0-9]{1,3}):[0-9]+$")

    CORS(
        app,
        resources={r"/*": {"origins": static_origins + [lan_origin_pattern], "supports_credentials": True}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=True,
    )

    # 兜底：确保预检和实际响应都带上允许凭据等 CORS 头
    @app.after_request
    def _ensure_cors_headers(resp):  # type: ignore[override]
        origin = request.headers.get("Origin")
        if origin:
            # 无条件回显 Origin 与 Credentials，确保浏览器通过预检
            resp.headers["Access-Control-Allow-Origin"] = origin
            vary = resp.headers.get("Vary")
            resp.headers["Vary"] = (vary + ", Origin") if vary else "Origin"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization")
            resp.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        # 强制为会话 Cookie 附加 SameSite/Secure 以支持跨端口请求
        try:
            session_cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
            cookies = resp.headers.getlist("Set-Cookie")
            if cookies:
                new_cookies = []
                for c in cookies:
                    if c.startswith(f"{session_cookie_name}="):
                        if "SameSite" not in c:
                            same_site = "None" if app.config.get("SESSION_COOKIE_SECURE") else "Lax"
                            c += f"; SameSite={same_site}"
                        if app.config.get("SESSION_COOKIE_SECURE") and "Secure" not in c:
                            c += "; Secure"
                    new_cookies.append(c)
                # 先删除再重新设置，避免重复
                del resp.headers["Set-Cookie"]
                for c in new_cookies:
                    resp.headers.add("Set-Cookie", c)
        except Exception:
            pass
        return resp

    # 统一处理所有 OPTIONS 预检
    @app.route("/", defaults={"path": ""}, methods=["OPTIONS"])  # type: ignore[misc]
    @app.route("/<path:path>", methods=["OPTIONS"])  # type: ignore[misc]
    def _options_ok(path: str):
        origin = request.headers.get("Origin")
        resp = make_response("", 204)
        if origin:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return resp

    # 模型导入以便迁移能发现模型
    from .models import (  # noqa: F401  (只为注册模型到元数据)
        User,
        Shop,
        Message,
        KnowledgeBaseItem,
        KnowledgeVector,
        AIReply,
        ReplyTemplate,
        AuditQueueItem,
        StatisticsDaily,
    )

    # 配置 user_loader
    @login_manager.user_loader
    def load_user(user_id: str):
        """从数据库加载用户（使用原生引擎，避免绑定问题）"""
        try:
            from flask import current_app
            from sqlalchemy import create_engine, text
            database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
            engine = create_engine(database_url)
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id, username, role FROM users WHERE id = :i LIMIT 1"),
                    {"i": int(user_id)},
                ).mappings().first()
            if not row:
                return None
            class UserObj:
                def __init__(self, row):
                    self.id = row["id"]
                    self.username = row["username"]
                    self.role = row["role"]
            from .api.auth import LoginUser
            return LoginUser(UserObj(row))
        except Exception:
            return None

    # 动态选择API模式
    try:
        from .api.adapters import should_use_simple_api, get_api_mode
        from .api.simple import api_bp as simple_api_bp
        from .api import api_bp as full_api_bp
        
        # 注册API适配器端点
        from .api.adapters import api_bp as adapter_api_bp
        app.register_blueprint(adapter_api_bp, url_prefix="/api", name="api_adapters")
        
        # 根据数据库状态选择API模式
        if should_use_simple_api():
            app.register_blueprint(simple_api_bp, url_prefix="/api", name="api_simple")
            print(f"使用简化版API模块 (模式: {get_api_mode()})")
        else:
            app.register_blueprint(full_api_bp, url_prefix="/api", name="api_full")
            print(f"使用完整版API模块 (模式: {get_api_mode()})")
            
    except ImportError as e:
        # 回退到简化版API
        from .api.simple import api_bp  # noqa: E402
        app.register_blueprint(api_bp, url_prefix="/api", name="api_simple")
        print(f"回退到简化版API模块: {e}")
    except Exception as e:
        # 最终回退
        from .api import api_bp  # noqa: E402
        app.register_blueprint(api_bp, url_prefix="/api", name="api_full")
        print(f"最终回退到完整版API模块: {e}")

    # 启动后台调度（仅在非测试环境）
    if not app.config.get("TESTING"):
        try:
            from .services.scheduler import start_scheduler  # noqa: E402
            start_scheduler(app)
        except Exception:
            # 调度器失败不应影响主服务可用性
            pass

    @app.get("/health")
    def health_check():
        """健康检查接口"""
        try:
            # 检查数据库连接
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception:
            db_status = "error"
        
        # 使用数据库管理器进行更详细的健康检查
        try:
            from .utils.db_manager import get_database_url
            health_info = db_manager.health_check(get_database_url())
            if health_info['status'] == 'healthy':
                db_status = "ok"
            else:
                db_status = "error"
        except Exception:
            db_status = "error"
        
        # 获取数据库健康监控状态
        db_health_status = {}
        try:
            from .services.db_health import get_db_health_status
            db_health_status = get_db_health_status()
        except Exception:
            pass
        
        try:
            # 检查OCR服务（检查PaddleOCR模块是否可导入）
            from paddleocr import PaddleOCR
            ocr_status = "ok"
        except ImportError:
            ocr_status = "not_installed"
        except Exception:
            ocr_status = "error"
        
        try:
            # 检查AI服务（检查环境变量）
            import os
            ai_services = []
            if os.environ.get("OPENAI_API_KEY"):
                ai_services.append("openai")
            if os.environ.get("QWEN_API_KEY"):
                ai_services.append("qwen")
            if os.environ.get("ERNIE_API_KEY"):
                ai_services.append("ernie")
            ai_status = "ok" if ai_services else "no_config"
        except Exception:
            ai_status = "error"
        
        # 检查调度器状态
        try:
            from .services.scheduler import _scheduler
            scheduler_status = "ok" if _scheduler and _scheduler.running else "stopped"
        except Exception:
            scheduler_status = "error"
        
        # 计算整体状态
        overall_status = "ok"
        if db_status != "ok":
            overall_status = "error"
        elif ocr_status == "error" or ai_status == "error" or scheduler_status == "error":
            overall_status = "warning"
        
        # 获取性能监控数据
        performance_data = {}
        try:
            from .utils.query_optimizer import get_query_performance_report
            from .utils.connection_pool import get_pool_health_report
            from .utils.cache_manager import get_cache_stats
            
            performance_data = {
                "query_performance": get_query_performance_report(),
                "connection_pool": get_pool_health_report(),
                "cache_stats": get_cache_stats()
            }
        except Exception as e:
            performance_data = {"error": str(e)}
        
        return jsonify({
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "ocr": ocr_status,
                "ai": ai_status,
                "scheduler": scheduler_status
            },
            "ai_services": ai_services if ai_status == "ok" else [],
            "db_health": db_health_status,
            "performance": performance_data,
            "message": "服务运行正常" if overall_status == "ok" else "部分服务异常"
        })

    @app.get("/")
    def index():
        # 若存在打包后的前端，则默认返回前端首页；否则返回服务信息
        index_html = os.path.join(app.config["STATIC_DIST"], "index.html")
        if os.path.exists(index_html):
            return send_from_directory(app.config["STATIC_DIST"], "index.html")
        return jsonify({
            "service": "taobao-smart-cs-backend",
            "env": os.environ.get("FLASK_ENV", "production"),
        })

    # SPA 路由回退：非 /api 的路径都回到 index.html（前端路由接管）
    @app.route("/<path:path>")
    def serve_spa(path: str):
        if path.startswith("api/"):
            # 交给 API 蓝图处理，由于前缀为 /api，这里不覆盖
            return ("", 404)
        file_path = os.path.join(app.config["STATIC_DIST"], path)
        if os.path.isfile(file_path):
            return send_from_directory(app.config["STATIC_DIST"], path)
        return send_from_directory(app.config["STATIC_DIST"], "index.html")

    return app


if __name__ == "__main__":
    # 方便本地调试: 固定默认端口为 5002
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5002)))


