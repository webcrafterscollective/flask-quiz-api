# manage_db.py
"""
Programmatic migration runner — useful when flask CLI can't find the app.
Run with: python manage_db.py init/migrate/upgrade/create_admin
Examples:
  python manage_db.py init
  python manage_db.py migrate
  python manage_db.py upgrade
  python manage_db.py create_admin
"""

import sys
import os
from flask_migrate import init as _init, migrate as _migrate, upgrade as _upgrade
from app import create_app
from app.extensions import db
from app.models import User
from datetime import datetime

def ensure_app():
    # create app using same factory
    app = create_app()
    return app

def do_init(app):
    # create migrations folder if not exists by calling flask_migrate.init
    with app.app_context():
        _init(directory="migrations")
        print("migrations/ created (init)")

def do_migrate(app, message="auto"):
    with app.app_context():
        res = _migrate(message=message, directory="migrations")
        print("migrate:", res)

def do_upgrade(app):
    with app.app_context():
        _upgrade(directory="migrations")
        print("upgrade applied")

def do_create_admin(app):
    with app.app_context():
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('ADMIN_PASSWORD', 'adminpass')
        if User.query.filter_by(username=username).first():
            print("admin already exists")
            return
        u = User(username=username, email=email, role='admin')
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        print("admin created:", username)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py init|migrate|upgrade|create_admin")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    app = ensure_app()
    if cmd == "init":
        do_init(app)
    elif cmd == "migrate":
        do_migrate(app, message="init")
    elif cmd == "upgrade":
        do_upgrade(app)
    elif cmd == "create_admin":
        do_create_admin(app)
    else:
        print("Unknown command", cmd)
