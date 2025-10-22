from __future__ import annotations

from houduan.app import create_app
from houduan.models import User


def main() -> None:
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if not users:
            print("NO_USERS")
            return
        for u in users:
            # id, username, role, shop_id
            print(f"{u.id}\t{u.username}\t{u.role}\t{u.shop_id}")


if __name__ == "__main__":
    main()


