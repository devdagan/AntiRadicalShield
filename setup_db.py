from app import db, User, Product



# Run this script once to initialize the database and add products

db.drop_all()

db.create_all()



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



print("Database initialized with products!")

