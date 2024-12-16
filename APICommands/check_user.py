# APICommands/check_user.py

import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import User

def check_user(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User Found:\n"
                  f"Name: {user.first_name} {user.last_name}\n"
                  f"Email: {user.email}\n"
                  f"Role: {user.role}\n"
                  f"Address: {user.address_line1}, {user.address_line2 or 'N/A'}, {user.city}, {user.state}, {user.zip_code}, {user.country}\n"
                  f"Phone: {user.phone_number}")
        else:
            print(f"User with email '{email}' not found.")

if __name__ == "__main__":
    # You can pass the email as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python3 check_user.py <email>")
    else:
        email = sys.argv[1]
        check_user(email)
