# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, SQLALCHEMY_TRACK_MODIFICATIONS
from extensions import db, bcrypt, login_manager, migrate
from models import User, Product, Order, OrderItem
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from api import api_bp  # Import after initializing extensions

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)  # Initialize Flask-Migrate
login_manager.login_view = 'login'

# Register the API blueprint
app.register_blueprint(api_bp)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        display_name = request.form.get('display_name')
        date_of_birth = request.form.get('date_of_birth')
        address_line1 = request.form.get('address_line1')
        address_line2 = request.form.get('address_line2')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        country = request.form.get('country')
        phone_number = request.form.get('phone_number')

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already in use", "danger")
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email,
            password=hashed_pw,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            date_of_birth=date_of_birth,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            phone_number=phone_number
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('product_list.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    session['cart'] = cart
    flash(f"{product.name} added to cart.", "success")
    return redirect(url_for('product_detail', product_id=product_id))


@app.route('/cart')
def cart():
    if 'cart' not in session or len(session['cart']) == 0:
        return render_template('cart.html', items=[], total=0)
    cart = session['cart']
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal
            })
    return render_template('cart.html', items=items, total=total)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', {})
    for key in list(cart.keys()):
        new_qty = request.form.get(f'qty_{key}')
        if new_qty:
            cart[key] = int(new_qty)
    session['cart'] = cart
    flash("Cart updated.", "info")
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Process payment here
        session['cart'] = {}
        flash("Order placed successfully!", "success")
        return redirect(url_for('home'))
    if 'cart' not in session or len(session['cart']) == 0:
        flash("Your cart is empty.", "info")
        return redirect(url_for('cart'))
    cart = session['cart']
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal
            })
    return render_template('checkout.html', items=items, total=total)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update user details
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.display_name = request.form.get('display_name')
        current_user.date_of_birth = request.form.get('date_of_birth')
        current_user.address_line1 = request.form.get('address_line1')
        current_user.address_line2 = request.form.get('address_line2')
        current_user.city = request.form.get('city')
        current_user.state = request.form.get('state')
        current_user.zip_code = request.form.get('zip_code')
        current_user.country = request.form.get('country')
        current_user.phone_number = request.form.get('phone_number')

        # Handle email changes (optional)
        new_email = request.form.get('email')
        if new_email and new_email != current_user.email:
            # Check if new email is taken
            if User.query.filter_by(email=new_email).first():
                flash("Email already in use", "danger")
                return redirect(url_for('profile'))
            current_user.email = new_email

        # Handle password change if requested
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if new_password or confirm_new_password:
            # If either is provided, validate old password and confirm match
            if not old_password or not bcrypt.check_password_hash(current_user.password, old_password):
                flash("Old password is incorrect.", "danger")
                return redirect(url_for('profile'))
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for('profile'))
            # Update password
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)


if __name__ == '__main__':
    app.run(debug=True)
