
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse, urljoin

from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, session, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_
from werkzeug.security import (
    generate_password_hash, check_password_hash
)


# =========================================
# APPLICATION CONFIGURATION
# =========================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "development-only-change-this-before-deployment"
)

database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///lolabmart.db"
)

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("RENDER") == "true"
    or os.environ.get("FLASK_ENV") == "production"
)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."


# =========================================
# CONSTANTS
# =========================================

MARKETPLACE_ORIGIN = "Lolab Valley"

ALLOWED_CATEGORIES = [
    "Local Produce",
    "Handmade Crafts",
    "Food Products",
    "Clothing & Textiles",
    "Other"
]


# =========================================
# DATABASE MODELS
# =========================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80), unique=True, nullable=False
    )

    email = db.Column(
        db.String(120), unique=True, nullable=False
    )

    password_hash = db.Column(
        db.String(255), nullable=False
    )

    role = db.Column(
        db.String(20), default="customer", nullable=False
    )

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )

    products = db.relationship(
        "Product", backref="seller", lazy=True
    )

    orders = db.relationship(
        "Order", backref="customer", lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash, password
        )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150), nullable=False
    )

    description = db.Column(
        db.Text, nullable=False
    )

    price = db.Column(
        db.Numeric(10, 2), nullable=False
    )

    category = db.Column(
        db.String(80), nullable=False
    )

    image_url = db.Column(
        db.String(500), nullable=True
    )

    stock = db.Column(
        db.Integer, default=0, nullable=False
    )

    origin = db.Column(
        db.String(100),
        default=MARKETPLACE_ORIGIN,
        nullable=False
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    total_amount = db.Column(
        db.Numeric(10, 2), nullable=False
    )

    shipping_address = db.Column(
        db.Text, nullable=False
    )

    status = db.Column(
        db.String(30), default="Pending", nullable=False
    )

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=True
    )

    product_name = db.Column(
        db.String(150), nullable=False
    )

    quantity = db.Column(
        db.Integer, nullable=False
    )

    unit_price = db.Column(
        db.Numeric(10, 2), nullable=False
    )


# =========================================
# LOGIN MANAGER
# =========================================

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# =========================================
# TEMPLATE GLOBALS
# =========================================

@app.context_processor
def inject_globals():
    cart = session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    cart_count = sum(
        int(quantity)
        for quantity in cart.values()
        if str(quantity).isdigit()
    )

    return {
        "now_year": datetime.now().year,
        "cart_count": cart_count
    }


# =========================================
# HELPER FUNCTIONS
# =========================================

def valid_image_url(value):
    if not value:
        return True

    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )
    except ValueError:
        return False


def get_cart_items():
    cart_data = session.get("cart", {})

    if not isinstance(cart_data, dict):
        return [], Decimal("0.00")

    cart_items = []
    total = Decimal("0.00")

    for product_id, quantity in cart_data.items():
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (ValueError, TypeError):
            continue

        if quantity < 1:
            continue

        product = Product.query.filter_by(
            id=product_id,
            origin=MARKETPLACE_ORIGIN
        ).first()

        if product is None:
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return cart_items, total


def safe_next_url(target):
    if not target:
        return None

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    if (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
        and target.startswith("/")
        and not target.startswith("//")
        and "\\" not in target
    ):
        return target

    return None


def require_role(role):
    if not current_user.is_authenticated:
        abort(401)

    if current_user.role != role:
        abort(403)


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():
    products = Product.query.filter_by(
        origin=MARKETPLACE_ORIGIN
    ).order_by(
        Product.created_at.desc()
    ).limit(8).all()

    return render_template(
        "index.html",
        products=products
    )


# =========================================
# PRODUCT MARKETPLACE
# =========================================

@app.route("/products")
def products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = Product.query.filter_by(
        origin=MARKETPLACE_ORIGIN
    )

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter_by(category=category)

    product_list = query.order_by(
        Product.created_at.desc()
    ).all()

    categories = [
        row[0]
        for row in db.session.query(
            Product.category
        ).filter_by(
            origin=MARKETPLACE_ORIGIN
        ).distinct().all()
    ]

    return render_template(
        "products.html",
        products=product_list,
        categories=categories,
        search=search,
        category=category,
        selected_category=category
    )


# =========================================
# PRODUCT DETAILS
# =========================================

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.filter_by(
        id=product_id,
        origin=MARKETPLACE_ORIGIN
    ).first_or_404()

    return render_template(
        "product_detail.html",
        product=product
    )


# =========================================
# REGISTRATION
# =========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get(
            "username", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")
        role = request.form.get("role", "customer")

        if not username or not email or not password:
            flash("Please complete all fields.", "error")
            return redirect(url_for("register"))

        if len(username) < 3 or len(username) > 80:
            flash(
                "Username must contain 3 to 80 characters.",
                "error"
            )
            return redirect(url_for("register"))

        if len(password) < 8:
            flash(
                "Password must be at least 8 characters.",
                "error"
            )
            return redirect(url_for("register"))

        if role not in ("customer", "seller"):
            flash("Invalid account type.", "error")
            return redirect(url_for("register"))

        if (
            "@" not in email
            or len(email) > 120
            or " " in email
        ):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("register"))

        existing = User.query.filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

        if existing:
            flash(
                "Username or email already exists.",
                "error"
            )
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            role=role
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "Account created successfully. Please log in.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):
            login_user(user)

            flash(
                f"Welcome to LolabMart, {user.username}!",
                "success"
            )

            next_page = safe_next_url(
                request.args.get("next", "")
            )

            if next_page:
                return redirect(next_page)

            if user.role == "seller":
                return redirect(url_for("seller_dashboard"))

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# =========================================
# LOGOUT
# =========================================

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.pop("cart", None)

    flash("You have logged out.", "success")

    return redirect(url_for("home"))


# =========================================
# SHOPPING CART
# =========================================

@app.route("/cart")
def cart():
    cart_items, total = get_cart_items()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.filter_by(
        id=product_id,
        origin=MARKETPLACE_ORIGIN
    ).first_or_404()

    if product.stock <= 0:
        flash(
            "This product is currently unavailable.",
            "error"
        )
        return redirect(
            url_for("product_detail", product_id=product.id)
        )

    cart_data = session.get("cart", {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    key = str(product_id)

    try:
        current_quantity = int(cart_data.get(key, 0))
    except (ValueError, TypeError):
        current_quantity = 0

    current_quantity = max(current_quantity, 0)

    if current_quantity >= product.stock:
        flash("Available stock limit reached.", "error")
    else:
        cart_data[key] = current_quantity + 1
        session["cart"] = cart_data
        session.modified = True

        flash("Product added to your cart.", "success")

    return redirect(url_for("cart"))


@app.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    product = Product.query.filter_by(
        id=product_id,
        origin=MARKETPLACE_ORIGIN
    ).first_or_404()

    quantity = request.form.get("quantity", type=int)

    cart_data = session.get("cart", {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    key = str(product_id)

    if quantity is None or quantity < 1:
        cart_data.pop(key, None)

    elif quantity > product.stock:
        flash(
            "Quantity exceeds available stock.",
            "error"
        )

    else:
        cart_data[key] = quantity

    session["cart"] = cart_data
    session.modified = True

    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart_data = session.get("cart", {})

    if not isinstance(cart_data, dict):
        cart_data = {}

    cart_data.pop(str(product_id), None)

    session["cart"] = cart_data
    session.modified = True

    flash("Product removed from cart.", "success")

    return redirect(url_for("cart"))


# =========================================
# CHECKOUT
# =========================================

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    require_role("customer")

    cart_items, total = get_cart_items()

    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("products"))

    if request.method == "POST":
        address = request.form.get(
            "shipping_address", ""
        ).strip()

        if not address or len(address) > 1000:
            flash(
                "Please enter a valid delivery address.",
                "error"
            )
            return redirect(url_for("checkout"))

        try:
            order_items_to_create = []
            verified_total = Decimal("0.00")

            for item in cart_items:
                product = Product.query.filter_by(
                    id=item["product"].id,
                    origin=MARKETPLACE_ORIGIN
                ).with_for_update().first()

                quantity = item["quantity"]

                if product is None or product.stock < quantity:
                    raise ValueError(
                        f"Insufficient stock for "
                        f"{item['product'].name}."
                    )

                product.stock -= quantity

                verified_total += product.price * quantity

                order_items_to_create.append({
                    "product": product,
                    "quantity": quantity
                })

            order = Order(
                customer_id=current_user.id,
                total_amount=verified_total,
                shipping_address=address,
                status="Pending"
            )

            db.session.add(order)
            db.session.flush()

            for item in order_items_to_create:
                product = item["product"]

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item["quantity"],
                    unit_price=product.price
                )

                db.session.add(order_item)

            db.session.commit()

            session.pop("cart", None)

            flash(
                "Your order has been placed successfully!",
                "success"
            )

            return redirect(url_for("my_orders"))

        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
            return redirect(url_for("cart"))

        except Exception:
            db.session.rollback()
            app.logger.exception("Checkout failed")

            flash(
                "Unable to place your order. Please try again.",
                "error"
            )

            return redirect(url_for("cart"))

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )


# =========================================
# CUSTOMER ORDERS
# =========================================

@app.route("/my-orders")
@login_required
def my_orders():
    require_role("customer")

    orders = Order.query.filter_by(
        customer_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )


# =========================================
# SELLER DASHBOARD
# =========================================

@app.route("/seller")
@login_required
def seller_dashboard():
    require_role("seller")

    products = Product.query.filter_by(
        seller_id=current_user.id,
        origin=MARKETPLACE_ORIGIN
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "seller_dashboard.html",
        products=products
    )


# =========================================
# SELLER: CREATE PRODUCT
# =========================================

@app.route("/seller/product/create", methods=["GET", "POST"])
@login_required
def create_product():
    require_role("seller")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get(
            "description", ""
        ).strip()

        category = request.form.get(
            "category", ""
        ).strip()

        image_url = request.form.get(
            "image_url", ""
        ).strip()

        try:
            price = Decimal(
                request.form.get("price", "0")
            )

            stock = int(
                request.form.get("stock", "0")
            )

        except (ValueError, TypeError, InvalidOperation):
            flash(
                "Enter a valid price and stock quantity.",
                "error"
            )
            return redirect(url_for("create_product"))

        if (
            not name
            or len(name) > 150
            or not description
            or len(description) > 2000
            or category not in ALLOWED_CATEGORIES
            or not price.is_finite()
            or price <= 0
            or price > Decimal("99999999.99")
            or stock < 0
            or stock > 1000000
            or len(image_url) > 500
            or not valid_image_url(image_url)
        ):
            flash(
                "Please enter valid product information.",
                "error"
    )
            return redirect(url_for("create_product"))

        product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            stock=stock,
            image_url=image_url or None,
            origin=MARKETPLACE_ORIGIN,
            seller_id=current_user.id
        )

        db.session.add(product)
        db.session.commit()

        flash(
            "Your Lolab Valley product has been listed.",
            "success"
        )

        return redirect(url_for("seller_dashboard"))

    return render_template(
        "create_product.html",
        categories=ALLOWED_CATEGORIES
    )
    # =========================================
# SELLER: DELETE PRODUCT
# =========================================

@app.route(
    "/seller/product/delete/<int:product_id>",
    methods=["POST"]
)
@login_required
def delete_product(product_id):
    require_role("seller")

    product = Product.query.filter_by(
        id=product_id,
        seller_id=current_user.id,
        origin=MARKETPLACE_ORIGIN
    ).first_or_404()

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")

    return redirect(url_for("seller_dashboard"))

# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route("/admin")
@login_required
def admin_dashboard():
    require_role("admin")

    total_users = User.query.count()

    total_products = Product.query.filter_by(
        origin=MARKETPLACE_ORIGIN
    ).count()

    total_orders = Order.query.count()

    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()

    users = User.query.order_by(
        User.created_at.desc()
    ).limit(20).all()

    products = Product.query.order_by(
        Product.created_at.desc()
    ).limit(20).all()
    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        recent_orders=recent_orders,
        users=users,
        products=products
    )
    
# =========================================
# ERROR HANDLERS
# =========================================

@app.errorhandler(403)
def forbidden(error):
    return render_template(
        "403.html"
    ), 403


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "404.html"
    ), 404


# =========================================
# DATABASE INITIALIZATION
# =========================================

with app.app_context():
    db.create_all()
    





    
