# APICommands/set_admin.py

import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import User

with app.app_context():
    user = User.query.filter_by(email="devijino8@gmail.com").first()
    if user:
        user.role = "admin"
        db.session.commit()
        print(f"User {user.email} has been promoted to admin.")
    else:
        print("User with email 'devijino8@gmail.com' not found.")
