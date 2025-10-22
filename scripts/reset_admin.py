from __future__ import annotations
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash

from houduan.app import create_app, db
from houduan.models import User


def main() -> None:
    app = create_app()
    with app.app_context():
        # 清空用户表
        User.query.delete()
        db.session.commit()

        # 创建 admin/admin
        admin = User(
            username="admin",
            role="superadmin",
            password_hash=generate_password_hash("admin"),
        )
        db.session.add(admin)
        db.session.commit()
        print("RESET_OK")


if __name__ == "__main__":
    main()


