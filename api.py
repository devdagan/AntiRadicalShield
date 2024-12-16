import datetime
import jwt
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from extensions import db, bcrypt
from models import User, Product

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')


def create_token(user_id, role, expires_in=3600):
    """
    Create a JWT token for the given user_id and role.
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


def token_required(f):
    """
    Decorator to protect routes that require a valid JWT token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
            user_role = data.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(user_id, user_role, *args, **kwargs)
    return decorated


def admin_required(f):
    """
    Decorator to ensure that the user has admin privileges.
    """
    @wraps(f)
    def decorated(user_id, user_role, *args, **kwargs):
        if user_role != 'admin':
            return jsonify({'error': 'Admin access required!'}), 403
        return f(user_id, *args, **kwargs)
    return decorated


@api_bp.route('/register', methods=['POST'])
def api_register():
    """
    API endpoint to register a new user.
    Expects JSON data with required user fields.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    required_fields = ['email', 'password', 'first_name', 'last_name', 'address_line1', 'city', 'state', 'zip_code', 'country', 'phone_number']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already in use'}), 400

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        email=data['email'],
        password=hashed_pw,
        first_name=data['first_name'],
        last_name=data['last_name'],
        display_name=data.get('display_name'),
        date_of_birth=data.get('date_of_birth'),
        address_line1=data['address_line1'],
        address_line2=data.get('address_line2'),
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        country=data['country'],
        phone_number=data['phone_number'],
        role='user'  # Default role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@api_bp.route('/login', methods=['POST'])
def api_login():
    """
    API endpoint to login a user.
    Expects JSON data with 'email' and 'password'.
    Returns a JWT token upon successful authentication.
    """
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_token(user.id, user.role)
        return jsonify({'message': 'Login successful', 'token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401


@api_bp.route('/profile', methods=['GET'])
@token_required
def api_get_profile(user_id, user_role):
    """
    API endpoint to get the profile of the authenticated user.
    Requires a valid JWT token.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user_data = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'display_name': user.display_name,
        'date_of_birth': user.date_of_birth,
        'address_line1': user.address_line1,
        'address_line2': user.address_line2,
        'city': user.city,
        'state': user.state,
        'zip_code': user.zip_code,
        'country': user.country,
        'phone_number': user.phone_number,
        'role': user.role
    }
    return jsonify(user_data), 200


@api_bp.route('/profile', methods=['PUT'])
@token_required
def api_update_profile(user_id, user_role):
    """
    API endpoint to update the profile of the authenticated user.
    Requires a valid JWT token and JSON data with fields to update.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    # Update fields if present
    if 'email' in data and data['email'] != user.email:
        # Check if new email is taken
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.display_name = data.get('display_name', user.display_name)
    user.date_of_birth = data.get('date_of_birth', user.date_of_birth)
    user.address_line1 = data.get('address_line1', user.address_line1)
    user.address_line2 = data.get('address_line2', user.address_line2)
    user.city = data.get('city', user.city)
    user.state = data.get('state', user.state)
    user.zip_code = data.get('zip_code', user.zip_code)
    user.country = data.get('country', user.country)
    user.phone_number = data.get('phone_number', user.phone_number)

    # Handle password change if provided
    if 'old_password' in data and 'new_password' in data:
        if not bcrypt.check_password_hash(user.password, data['old_password']):
            return jsonify({'error': 'Old password is incorrect'}), 400
        user.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200


@api_bp.route('/products', methods=['GET'])
def api_get_products():
    """
    API endpoint to retrieve all products.
    Publicly accessible.
    """
    products = Product.query.all()
    product_list = []
    for p in products:
        product_list.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'image_url': p.image_url
        })
    return jsonify(product_list), 200


@api_bp.route('/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    """
    API endpoint to retrieve a single product by ID.
    Publicly accessible.
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url
    }
    return jsonify(product_data), 200


@api_bp.route('/products', methods=['POST'])
@token_required
@admin_required
def api_create_product(user_id):
    """
    API endpoint to create a new product.
    Requires a valid JWT token and admin privileges.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    required_fields = ['name', 'description', 'price', 'image_url']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        price = float(data['price'])
    except ValueError:
        return jsonify({'error': 'Price must be a number'}), 400

    product = Product(
        name=data['name'],
        description=data['description'],
        price=price,
        image_url=data['image_url']
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created', 'id': product.id}), 201


@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
@admin_required
def api_update_product(user_id, product_id):
    """
    API endpoint to update an existing product by ID.
    Requires a valid JWT token and admin privileges.
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    if 'price' in data:
        try:
            product.price = float(data['price'])
        except ValueError:
            return jsonify({'error': 'Price must be a number'}), 400
    product.image_url = data.get('image_url', product.image_url)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200


@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
@admin_required
def api_delete_product(user_id, product_id):
    """
    API endpoint to delete a product by ID.
    Requires a valid JWT token and admin privileges.
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
