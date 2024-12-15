# APICommands/check_user.py

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
        print(f"User Found:\n"
              f"Name: {user.first_name} {user.last_name}\n"
              f"Email: {user.email}\n"
              f"Role: {user.role}\n"
              f"Address: {user.address_line1}, {user.address_line2 or 'N/A'}, {user.city}, {user.state}, {user.zip_code}, {user.country}\n"
              f"Phone: {user.phone_number}")
    else:
        print("User with email 'devijino8@gmail.com' not found.")
