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
# (same as before)

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

# ==================== ADD SALE ROUTE ====================
@app.route('/add_sale')
def add_sale():
    """Add Sale placeholder"""
    return render_template('add_sale.html')  # You need to create this template

# ==================== SUPPLIERS ROUTE ====================
@app.route('/suppliers')
def suppliers():
    """View all suppliers"""
    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)  # Create a suppliers template

# ==================== CUSTOMERS ROUTE ====================
@app.route('/customers')
def customers():
    """View all customers"""
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)  # Create a customers template

# ==================== FINANCE ROUTE ====================
@app.route('/finance')
def finance():
    """View finance details"""
    expenses = Expense.query.all()
    return render_template('finance.html', expenses=expenses)  # Create a finance template

# ==================== REPORTS ROUTE ====================
@app.route('/reports')
def reports():
    """View sales and product reports"""
    # Placeholder for reports
    return render_template('reports.html')  # You need to create this template

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
    # Same as before
    pass

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
