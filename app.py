import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cosmetic-shop-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100))
    category = db.Column(db.String(50))  # makeup, skincare, hair, baby
    buying_price = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    supplier = db.relationship('Supplier', backref='products')
    sales = db.relationship('Sale', backref='product', lazy=True)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(100))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    products_supplied = db.Column(db.Text)  # Comma-separated list
    delivery_time = db.Column(db.String(50))  # e.g., "3-5 days"
    credit_terms = db.Column(db.String(50))  # e.g., "Net 30"
    last_price_list = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    products_bought = db.Column(db.Text)  # Comma-separated list
    skin_type = db.Column(db.String(100))  # dry, oily, combination, sensitive
    hair_type = db.Column(db.String(100))  # dry, oily, normal
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    purchases = db.relationship('Sale', backref='customer', lazy=True)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))  # cash, mpesa, card
    receipt_number = db.Column(db.String(50), unique=True)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    profit = db.Column(db.Float, default=0)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50))  # rent, transport, utilities, stock_purchase, other
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Dashboard - Overview of the shop"""
    # Get counts
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity <= Product.reorder_level).count()
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    
    # Get today's sales
    today = datetime.now().date()
    today_sales = Sale.query.filter(db.func.date(Sale.sale_date) == today).all()
    today_revenue = sum(sale.total_amount for sale in today_sales)
    today_profit = sum(sale.profit for sale in today_sales)
    
    # Get recent sales
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
    
    # Get low stock products
    low_stock_products = Product.query.filter(Product.quantity <= Product.reorder_level).limit(5).all()
    
    return render_template('index.html', 
                           total_products=total_products,
                           low_stock=low_stock,
                           total_customers=total_customers,
                           total_suppliers=total_suppliers,
                           today_revenue=today_revenue,
                           today_profit=today_profit,
                           recent_sales=recent_sales,
                           low_stock_products=low_stock_products)

# ==================== DATABASE INITIALIZATION ====================
@app.before_first_request
def initialize_db():
    """Ensure the database is initialized and tables are created"""
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist

# ==================== INVENTORY ROUTES ====================

@app.route('/inventory')
def inventory():
    """View all products in inventory"""
    products = Product.query.all()
    suppliers = Supplier.query.all()
    return render_template('inventory.html', products=products, suppliers=suppliers)

@app.route('/add_product', methods=['POST'])
def add_product():
    """Add a new product to inventory"""
    name = request.form.get('name')
    brand = request.form.get('brand')
    category = request.form.get('category')
    buying_price = float(request.form.get('buying_price', 0))
    selling_price = float(request.form.get('selling_price', 0))
    quantity = int(request.form.get('quantity', 0))
    reorder_level = int(request.form.get('reorder_level', 10))
    supplier_id = request.form.get('supplier_id')
    expiry_date = request.form.get('expiry_date')
    
    if expiry_date:
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
    
    product = Product(
        name=name,
        brand=brand,
        category=category,
        buying_price=buying_price,
        selling_price=selling_price,
        quantity=quantity,
        reorder_level=reorder_level,
        supplier_id=supplier_id,
        expiry_date=expiry_date
    )
    
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('inventory'))

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

