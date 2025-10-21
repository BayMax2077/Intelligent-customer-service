#!/usr/bin/env python3
"""测试登录功能"""
from houduan.app import create_app, db
from houduan.models import User
from houduan.utils.security import verify_password

app = create_app()
with app.app_context():
    # 查找admin用户
    user = db.session.query(User).filter_by(username='admin').first()
    print('User found:', user is not None)
    if user:
        print('Password hash:', user.password_hash[:50])
        print('Password verify:', verify_password(user.password_hash, 'admin'))
        print('User role:', user.role)
    else:
        print('Admin user not found, creating one...')
        from houduan.utils.security import hash_password
        admin = User(
            username='admin',
            password_hash=hash_password('admin'),
            role='superadmin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created')
