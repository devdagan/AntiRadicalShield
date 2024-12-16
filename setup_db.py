# setup_db.py

from app import app
from extensions import db
from models import User, Product
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    # Drop all tables (be cautious: this will erase existing data)
    db.drop_all()
    # Create all tables
    db.create_all()

    # Create an admin user
    admin_user = User(
        email="devdagan@gmail.com",
        password=bcrypt.generate_password_hash("SecureAdminPass123").decode('utf-8'),  # Choose a strong password
        first_name="Yossi",
        last_name="Dagan",
        display_name="YossiD",
        date_of_birth="1990-05-15",  # Format: YYYY-MM-DD
        address_line1="123 Admin Street",
        address_line2="Apt 456",
        city="Tel Aviv",
        state="Tel Aviv District",
        zip_code="60000",
        country="Israel",
        phone_number="+972-50-123-4567",
        role="admin"  # Assign admin role
    )

    db.session.add(admin_user)

    # Add sample products (10 Anti-Aging Products)
    products = [
        Product(
            name="Anti Radical Serum",
            description="A cutting-edge serum that neutralizes free radicals and reduces visible signs of aging.",
            price=49.99,
            image_url="/static/img/product1.jpg"
        ),
        Product(
            name="Youth Rejuvenation Cream",
            description="An advanced cream that lifts, hydrates, and restores youthful glow.",
            price=59.99,
            image_url="/static/img/product2.jpg"
        ),
        Product(
            name="Ultra Renewal Eye Gel",
            description="Targets dark circles, puffiness, and fine lines around the eyes.",
            price=39.99,
            image_url="/static/img/product3.jpg"
        ),
        Product(
            name="Collagen Boost Night Mask",
            description="Overnight mask that boosts collagen production and firms the skin.",
            price=69.99,
            image_url="/static/img/product4.jpg"
        ),
        Product(
            name="Vitamin C Radiance Toner",
            description="Brightens and evens out skin tone, preparing skin for next steps.",
            price=29.99,
            image_url="/static/img/product5.jpg"
        ),
        Product(
            name="Hyaluronic Acid Moisturizer",
            description="Deep hydration formula that plumps and smooths fine lines.",
            price=54.99,
            image_url="/static/img/product6.jpg"
        ),
        Product(
            name="Resveratrol Defense Lotion",
            description="High antioxidant lotion that shields against environmental stress.",
            price=64.99,
            image_url="/static/img/product7.jpg"
        ),
        Product(
            name="CoQ10 Repair Essence",
            description="Essence that revitalizes dull skin and enhances elasticity.",
            price=44.99,
            image_url="/static/img/product8.jpg"
        ),
        Product(
            name="Peptide Firming Serum",
            description="Concentrated serum with peptides to improve firmness and texture.",
            price=74.99,
            image_url="/static/img/product9.jpg"
        ),
        Product(
            name="Microalgae Detox Cleanser",
            description="Cleanser that gently removes impurities and protects the skin barrier.",
            price=24.99,
            image_url="/static/img/product10.jpg"
        )
    ]

    db.session.add_all(products)
    db.session.commit()

    print("Database initialized with admin user and products!")
