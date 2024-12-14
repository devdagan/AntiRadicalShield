from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, SQLALCHEMY_TRACK_MODIFICATIONS



app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS



db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = 'login'



class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password = db.Column(db.String(150), nullable=False)

    name = db.Column(db.String(150), nullable=False)



class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)

    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False)

    image_url = db.Column(db.String(255), nullable=False)



@login_manager.user_loader

def load_user(user_id):

    return User.query.get(int(user_id))



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

        name = request.form.get('name')

        if User.query.filter_by(email=email).first():

            flash("Email already in use", "danger")

        else:

            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = User(email=email, password=hashed_pw, name=name)

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



@app.route('/profile')

@login_required

def profile():

    return render_template('profile.html', user=current_user)



if __name__ == '__main__':

    app.run(debug=True)

