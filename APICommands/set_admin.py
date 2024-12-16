# APICommands/set_admin.py

import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import User

def set_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = "admin"
            db.session.commit()
            print(f"User {user.email} has been promoted to admin.")
        else:
            print(f"User with email '{email}' not found.")

if __name__ == "__main__":
    # You can pass the email as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python3 set_admin.py <email>")
    else:
        email = sys.argv[1]
        set_admin(email)
