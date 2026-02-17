import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
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
    category = db.Column(db.String(50))
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
    products_supplied = db.Column(db.Text)
    delivery_time = db.Column(db.String(50))
    credit_terms = db.Column(db.String(50))
    last_price_list = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    products_bought = db.Column(db.Text)
    skin_type = db.Column(db.String(100))
    hair_type = db.Column(db.String(100))
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
    payment_method = db.Column(db.String(20))
    receipt_number = db.Column(db.String(50), unique=True)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    profit = db.Column(db.Float, default=0)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== DATABASE INITIALIZATION ====================
with app.app_context():
    db.create_all()

# ==================== DASHBOARD ====================

@app.route('/')
def index():
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity <= Product.reorder_level).count()
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    today = datetime.now().date()
    today_sales = Sale.query.filter(db.func.date(Sale.sale_date) == today).all()
    today_revenue = sum(s.total_amount for s in today_sales)
    today_profit = sum(s.profit for s in today_sales)
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
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

# ==================== INVENTORY ====================

@app.route('/inventory')
def inventory():
    products = Product.query.all()
    suppliers = Supplier.query.all()
    return render_template('inventory.html', products=products, suppliers=suppliers)

@app.route('/add_product', methods=['POST'])
def add_product():
    expiry_date = request.form.get('expiry_date')
    product = Product(
        name=request.form.get('name'),
        brand=request.form.get('brand'),
        category=request.form.get('category'),
        buying_price=float(request.form.get('buying_price', 0)),
        selling_price=float(request.form.get('selling_price', 0)),
        quantity=int(request.form.get('quantity', 0)),
        reorder_level=int(request.form.get('reorder_level', 10)),
        supplier_id=request.form.get('supplier_id') or None,
        expiry_date=datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None
    )
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/edit_product/<int:id>', methods=['POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    product.name = request.form.get('name')
    product.brand = request.form.get('brand')
    product.category = request.form.get('category')
    product.buying_price = float(request.form.get('buying_price', 0))
    product.selling_price = float(request.form.get('selling_price', 0))
    product.quantity = int(request.form.get('quantity', 0))
    product.reorder_level = int(request.form.get('reorder_level', 10))
    product.supplier_id = request.form.get('supplier_id') or None
    expiry_date = request.form.get('expiry_date')
    product.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None
    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('inventory'))

# ==================== SALES ====================

@app.route('/sales')
def add_sale():
    products = Product.query.filter(Product.quantity > 0).all()
    customers = Customer.query.all()
    sales = Sale.query.order_by(Sale.sale_date.desc()).limit(50).all()
    return render_template('sales.html', products=products, customers=customers, sales=sales)

@app.route('/record_sale', methods=['POST'])
def record_sale():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    product = Product.query.get_or_404(product_id)
    if product.quantity < quantity:
        flash(f'Not enough stock! Only {product.quantity} units available.', 'danger')
        return redirect(url_for('add_sale'))
    total_amount = product.selling_price * quantity
    profit = (product.selling_price - product.buying_price) * quantity
    receipt_number = f'RCP-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    sale = Sale(
        product_id=product_id,
        customer_id=request.form.get('customer_id') or None,
        quantity=quantity,
        unit_price=product.selling_price,
        total_amount=total_amount,
        payment_method=request.form.get('payment_method'),
        receipt_number=receipt_number,
        profit=profit
    )
    product.quantity -= quantity
    db.session.add(sale)
    db.session.commit()
    flash(f'Sale recorded! Receipt: {receipt_number}', 'success')
    return redirect(url_for('add_sale'))

# ==================== CUSTOMERS ====================

@app.route('/customers')
def customers():
    all_customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers.html', customers=all_customers)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    customer = Customer(
        name=request.form.get('name'),
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        skin_type=request.form.get('skin_type'),
        hair_type=request.form.get('hair_type'),
        notes=request.form.get('notes')
    )
    db.session.add(customer)
    db.session.commit()
    flash('Customer added successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/delete_customer/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted.', 'success')
    return redirect(url_for('customers'))

# ==================== SUPPLIERS ====================

@app.route('/suppliers')
def suppliers():
    all_suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    return render_template('suppliers.html', suppliers=all_suppliers)

@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    supplier = Supplier(
        name=request.form.get('name'),
        contact=request.form.get('contact'),
        email=request.form.get('email'),
        address=request.form.get('address'),
        products_supplied=request.form.get('products_supplied'),
        delivery_time=request.form.get('delivery_time'),
        credit_terms=request.form.get('credit_terms'),
        last_price_list=request.form.get('last_price_list')
    )
    db.session.add(supplier)
    db.session.commit()
    flash('Supplier added successfully!', 'success')
    return redirect(url_for('suppliers'))

@app.route('/delete_supplier/<int:id>', methods=['POST'])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier deleted.', 'success')
    return redirect(url_for('suppliers'))

# ==================== FINANCE ====================

@app.route('/finance')
def finance():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    total_expenses = sum(e.amount for e in expenses)
    all_sales = Sale.query.all()
    total_revenue = sum(s.total_amount for s in all_sales)
    total_profit = sum(s.profit for s in all_sales)
    net_profit = total_profit - total_expenses
    return render_template('finance.html',
                           expenses=expenses,
                           total_expenses=total_expenses,
                           total_revenue=total_revenue,
                           total_profit=total_profit,
                           net_profit=net_profit)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    expense = Expense(
        date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
        category=request.form.get('category'),
        description=request.form.get('description'),
        amount=float(request.form.get('amount', 0))
    )
    db.session.add(expense)
    db.session.commit()
    flash('Expense recorded successfully!', 'success')
    return redirect(url_for('finance'))

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('finance'))

# ==================== REPORTS ====================

@app.route('/reports')
def reports():
    all_sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    total_revenue = sum(s.total_amount for s in all_sales)
    total_profit = sum(s.profit for s in all_sales)
    total_expenses = sum(e.amount for e in Expense.query.all())
    net_profit = total_profit - total_expenses
    top_products = db.session.query(
        Product.name,
        db.func.sum(Sale.quantity).label('total_sold'),
        db.func.sum(Sale.total_amount).label('total_revenue')
    ).join(Sale).group_by(Product.id).order_by(db.func.sum(Sale.total_amount).desc()).limit(5).all()
    return render_template('reports.html',
                           all_sales=all_sales,
                           total_revenue=total_revenue,
                           total_profit=total_profit,
                           total_expenses=total_expenses,
                           net_profit=net_profit,
                           top_products=top_products)

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
