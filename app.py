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

@app.route('/update_product/<int:id>', methods=['POST'])
def update_product(id):
    """Update a product"""
    product = Product.query.get_or_404(id)
    product.name = request.form.get('name')
    product.brand = request.form.get('brand')
    product.category = request.form.get('category')
    product.buying_price = float(request.form.get('buying_price', 0))
    product.selling_price = float(request.form.get('selling_price', 0))
    product.quantity = int(request.form.get('quantity', 0))
    product.reorder_level = int(request.form.get('reorder_level', 10))
    product.supplier_id = request.form.get('supplier_id')
    expiry_date = request.form.get('expiry_date')
    if expiry_date:
        product.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
    
    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    """Delete a product"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/update_stock/<int:id>', methods=['GET', 'POST'])
def update_stock(id):
    """Update stock quantity"""
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        quantity_change = int(request.form.get('quantity_change', 0))
        product.quantity += quantity_change
        db.session.commit()
        flash(f'Stock updated! New quantity: {product.quantity}', 'success')
        return redirect(url_for('inventory'))
    return render_template('update_stock.html', product=product)

# ==================== SALES/POS ROUTES ====================

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    """Record a new sale"""
    if request.method == 'POST':
        product_id = int(request.form.get('product_id'))
        customer_id = request.form.get('customer_id')
        if customer_id:
            customer_id = int(customer_id)
        quantity = int(request.form.get('quantity', 1))
        payment_method = request.form.get('payment_method')
        
        product = Product.query.get_or_404(product_id)
        
        if product.quantity < quantity:
            flash(f'Not enough stock! Available: {product.quantity}', 'error')
            return redirect(url_for('add_sale'))
        
        total_amount = product.selling_price * quantity
        profit = (product.selling_price - product.buying_price) * quantity
        
        # Generate receipt number
        last_sale = Sale.query.order_by(Sale.id.desc()).first()
        receipt_number = f"REC-{datetime.now().year}{datetime.now().month:02d}{(last_sale.id + 1) if last_sale else 1:05d}"
        
        sale = Sale(
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            unit_price=product.selling_price,
            total_amount=total_amount,
            payment_method=payment_method,
            receipt_number=receipt_number,
            profit=profit
        )
        
        # Update product quantity
        product.quantity -= quantity
        
        db.session.add(sale)
        db.session.commit()
        
        flash(f'Sale recorded! Receipt: {receipt_number}', 'success')
        return redirect(url_for('index'))
    
    products = Product.query.filter(Product.quantity > 0).all()
    customers = Customer.query.all()
    return render_template('add_sale.html', products=products, customers=customers)

@app.route('/sales')
def sales():
    """View all sales"""
    sales_list = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', sales=sales_list)

# ==================== SUPPLIER ROUTES ====================

@app.route('/suppliers')
def suppliers():
    """View all suppliers"""
    suppliers_list = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers_list)

@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    """Add a new supplier"""
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

@app.route('/update_supplier/<int:id>', methods=['POST'])
def update_supplier(id):
    """Update a supplier"""
    supplier = Supplier.query.get_or_404(id)
    supplier.name = request.form.get('name')
    supplier.contact = request.form.get('contact')
    supplier.email = request.form.get('email')
    supplier.address = request.form.get('address')
    supplier.products_supplied = request.form.get('products_supplied')
    supplier.delivery_time = request.form.get('delivery_time')
    supplier.credit_terms = request.form.get('credit_terms')
    supplier.last_price_list = request.form.get('last_price_list')
    
    db.session.commit()
    flash('Supplier updated successfully!', 'success')
    return redirect(url_for('suppliers'))

@app.route('/delete_supplier/<int:id>', methods=['POST'])
def delete_supplier(id):
    """Delete a supplier"""
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('suppliers'))

# ==================== CUSTOMER ROUTES ====================

@app.route('/customers')
def customers():
    """View all customers"""
    customers_list = Customer.query.all()
    return render_template('customers.html', customers=customers_list)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    """Add a new customer"""
    customer = Customer(
        name=request.form.get('name'),
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        products_bought=request.form.get('products_bought'),
        skin_type=request.form.get('skin_type'),
        hair_type=request.form.get('hair_type'),
        notes=request.form.get('notes')
    )
    db.session.add(customer)
    db.session.commit()
    flash('Customer added successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/update_customer/<int:id>', methods=['POST'])
def update_customer(id):
    """Update a customer"""
    customer = Customer.query.get_or_404(id)
    customer.name = request.form.get('name')
    customer.phone = request.form.get('phone')
    customer.email = request.form.get('email')
    customer.products_bought = request.form.get('products_bought')
    customer.skin_type = request.form.get('skin_type')
    customer.hair_type = request.form.get('hair_type')
    customer.notes = request.form.get('notes')
    
    db.session.commit()
    flash('Customer updated successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/delete_customer/<int:id>', methods=['POST'])
def delete_customer(id):
    """Delete a customer"""
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers'))

# ==================== FINANCE ROUTES ====================

@app.route('/finance')
def finance():
    """View finance/cashbook"""
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    
    # Calculate totals
    total_expenses = sum(e.amount for e in expenses)
    
    # Get sales for the period
    sales = Sale.query.all()
    total_sales = sum(s.total_amount for s in sales)
    total_profit = sum(s.profit for s in sales)
    
    return render_template('finance.html', 
                           expenses=expenses, 
                           total_expenses=total_expenses,
                           total_sales=total_sales,
                           total_profit=total_profit)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    """Add a new expense"""
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    expense = Expense(
        date=date,
        category=request.form.get('category'),
        description=request.form.get('description'),
        amount=float(request.form.get('amount'))
    )
    db.session.add(expense)
    db.session.commit()
    flash('Expense added successfully!', 'success')
    return redirect(url_for('finance'))

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    """Delete an expense"""
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('finance'))

# ==================== REPORTS ROUTES ====================

@app.route('/reports')
def reports():
    """View sales and profit reports"""
    # Get date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Sale.query
    
    if start_date:
        query = query.filter(Sale.sale_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Sale.sale_date <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
    
    sales = query.order_by(Sale.sale_date.desc()).all()
    
    total_revenue = sum(s.total_amount for s in sales)
    total_profit = sum(s.profit for s in sales)
    total_quantity = sum(s.quantity for s in sales)
    
    # Top selling products
    product_sales = {}
    for sale in sales:
        if sale.product_id in product_sales:
            product_sales[sale.product_id] += sale.quantity
        else:
            product_sales[sale.product_id] = sale.quantity
    
    top_products = []
    for product_id, qty in sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]:
        product = Product.query.get(product_id)
        if product:
            top_products.append({'product': product, 'quantity': qty})
    
    # Payment method breakdown
    payment_breakdown = {}
    for sale in sales:
        if sale.payment_method in payment_breakdown:
            payment_breakdown[sale.payment_method] += sale.total_amount
        else:
            payment_breakdown[sale.payment_method] = sale.total_amount
    
    return render_template('reports.html',
                           sales=sales,
                           total_revenue=total_revenue,
                           total_profit=total_profit,
                           total_quantity=total_quantity,
                           top_products=top_products,
                           payment_breakdown=payment_breakdown,
                           start_date=start_date,
                           end_date=end_date)

@app.route('/weekly_reports')
def weekly_reports():
    """View weekly reports"""
    # Get start of week (Monday)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    sales = Sale.query.filter(
        db.func.date(Sale.sale_date) >= start_of_week,
        db.func.date(Sale.sale_date) <= end_of_week
    ).all()
    
    # Daily sales breakdown
    daily_sales = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        daily_sales[day.strftime('%A')] = {'revenue': 0, 'profit': 0, 'quantity': 0}
    
    for sale in sales:
        day_name = sale.sale_date.strftime('%A')
        daily_sales[day_name]['revenue'] += sale.total_amount
        daily_sales[day_name]['profit'] += sale.profit
        daily_sales[day_name]['quantity'] += sale.quantity
    
    total_revenue = sum(s.total_amount for s in sales)
    total_profit = sum(s.profit for s in sales)
    total_quantity = sum(s.quantity for s in sales)
    
    # Category breakdown
    category_sales = {}
    for sale in sales:
        product = Product.query.get(sale.product_id)
        if product:
            cat = product.category or 'Uncategorized'
            if cat in category_sales:
                category_sales[cat] += sale.total_amount
            else:
                category_sales[cat] = sale.total_amount
    
    return render_template('weekly_reports.html',
                           daily_sales=daily_sales,
                           total_revenue=total_revenue,
                           total_profit=total_profit,
                           total_quantity=total_quantity,
                           category_sales=category_sales,
                           start_of_week=start_of_week,
                           end_of_week=end_of_week)

# ==================== API ROUTES ====================

@app.route('/api/products/low-stock')
def api_low_stock():
    """Get low stock products"""
    products = Product.query.filter(Product.quantity <= Product.reorder_level).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity,
        'reorder_level': p.reorder_level
    } for p in products])

@app.route('/api/sales/today')
def api_sales_today():
    """Get today's sales summary"""
    today = datetime.now().date()
    sales = Sale.query.filter(db.func.date(Sale.sale_date) == today).all()
    return jsonify({
        'count': len(sales),
        'revenue': sum(s.total_amount for s in sales),
        'profit': sum(s.profit for s in sales)
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
