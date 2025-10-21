"""
后端配置模块

优先从环境变量读取, 默认使用 SQLite 本地文件。
生产可设置:
- SECRET_KEY
- DATABASE_URL 例: mysql+pymysql://user:pass@host:3306/dbname?charset=utf8mb4
"""

from __future__ import annotations

import os


class Config:
    """Flask 应用配置。"""

    def __init__(self) -> None:
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            self.SQLALCHEMY_DATABASE_URI = database_url
        else:
            # 默认使用项目根目录下的 data/sqlite.db
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(data_dir, 'sqlite.db')}"

        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.JSON_AS_ASCII = False


