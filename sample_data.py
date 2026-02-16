from app import db, Product, Supplier, Customer, Expense, app
from datetime import datetime, timedelta

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Add Suppliers
    suppliers = [
        Supplier(
            name="Beauty Supplies Kenya",
            contact="John Mwangi",
            email="john@beautysupplies.co.ke",
            address="Mombasa Road, Nairobi",
            products_supplied="Lotions, Creams, Hair Products",
            delivery_time="3-5 days",
            credit_terms="Net 30"
        ),
        Supplier(
            name="Cosmetic Hub Africa",
            contact="Sarah Ochieng",
            email="sarah@cosmetic hub.co.ke",
            address="Westlands, Nairobi",
            products_supplied="Makeup, Skincare",
            delivery_time="2-3 days",
            credit_terms="Net 15"
        ),
        Supplier(
            name="Hair Care Direct",
            contact="Peter Oduya",
            email="peter@haircare.co.ke",
            address="Kasarani, Nairobi",
            products_supplied="Hair Products, Shampoos",
            delivery_time="1-2 days",
            credit_terms="Cash on Delivery"
        ),
        Supplier(
            name="Baby Care Distributors",
            contact="Mary Akinyi",
            email="mary@babycare.co.ke",
            address="Industrial Area, Nairobi",
            products_supplied="Baby Products, Diapers",
            delivery_time="2-4 days",
            credit_terms="Net 30"
        )
    ]
    db.session.add_all(suppliers)
    db.session.commit()
    
    # Add Products (Cosmetics)
    products = [
        # Skincare Products
        Product(name="Moisturizing Lotion", brand="Nivea", category="skincare", buying_price=250, selling_price=450, quantity=50, reorder_level=15, supplier_id=1),
        Product(name="Sunscreen SPF 50", brand="L'Oréal", category="skincare", buying_price=800, selling_price=1200, quantity=30, reorder_level=10, supplier_id=2),
        Product(name="Face Wash", brand="CeraVe", category="skincare", buying_price=600, selling_price=950, quantity=40, reorder_level=12, supplier_id=2),
        Product(name="Night Cream", brand="Olay", category="skincare", buying_price=900, selling_price=1400, quantity=25, reorder_level=8, supplier_id=2),
        Product(name="Body Lotion", brand="Vaseline", category="skincare", buying_price=180, selling_price=350, quantity=60, reorder_level=20, supplier_id=1),
        Product(name="Lip Balm", brand="Carmol", category="skincare", buying_price=80, selling_price=150, quantity=100, reorder_level=30, supplier_id=1),
        Product(name="Face Serum", brand="The Ordinary", category="skincare", buying_price=1200, selling_price=1800, quantity=20, reorder_level=5, supplier_id=2),
        
        # Makeup Products
        Product(name="Lipstick", brand="Maybelline", category="makeup", buying_price=350, selling_price=600, quantity=45, reorder_level=15, supplier_id=2),
        Product(name="Foundation", brand="Fenty Beauty", category="makeup", buying_price=1800, selling_price=2800, quantity=15, reorder_level=5, supplier_id=2),
        Product(name="Mascara", brand="L'Oréal", category="makeup", buying_price=450, selling_price=750, quantity=35, reorder_level=10, supplier_id=2),
        Product(name="Eyeliner", brand="Essence", category="makeup", buying_price=200, selling_price=400, quantity=50, reorder_level=15, supplier_id=2),
        Product(name="Blush", brand="NYX", category="makeup", buying_price=400, selling_price=700, quantity=30, reorder_level=10, supplier_id=2),
        Product(name="Concealer", brand="Maybelline", category="makeup", buying_price=500, selling_price=850, quantity=25, reorder_level=8, supplier_id=2),
        Product(name="Nail Polish", brand="Essie", category="makeup", buying_price=300, selling_price=550, quantity=40, reorder_level=12, supplier_id=2),
        
        # Hair Care Products
        Product(name="Shampoo", brand="Head & Shoulders", category="hair", buying_price=250, selling_price=450, quantity=80, reorder_level=25, supplier_id=3),
        Product(name="Hair Conditioner", brand="Pantene", category="hair", buying_price=280, selling_price=480, quantity=60, reorder_level=20, supplier_id=3),
        Product(name="Hair Oil", brand="Murray's", category="hair", buying_price=180, selling_price=350, quantity=70, reorder_level=20, supplier_id=3),
        Product(name="Hair Serum", brand="Argan", category="hair", buying_price=450, selling_price=750, quantity=40, reorder_level=12, supplier_id=3),
        Product(name="Hair Spray", brand="VO5", category="hair", buying_price=200, selling_price=380, quantity=50, reorder_level=15, supplier_id=3),
        Product(name="Hair Gel", brand="Ampro", category="hair", buying_price=120, selling_price=250, quantity=65, reorder_level=20, supplier_id=3),
        
        # Baby Care Products
        Product(name="Baby Lotion", brand="Johnson's", category="baby", buying_price=200, selling_price=380, quantity=50, reorder_level=15, supplier_id=4),
        Product(name="Baby Shampoo", brand="Gentle Baby", category="baby", buying_price=180, selling_price=350, quantity=55, reorder_level=18, supplier_id=4),
        Product(name="Baby Powder", brand="Fever", category="baby", buying_price=150, selling_price=300, quantity=60, reorder_level=20, supplier_id=4),
        Product(name="Diapers Size Small", brand="Pampers", category="baby", buying_price=800, selling_price=1200, quantity=25, reorder_level=10, supplier_id=4),
        Product(name="Diapers Size Medium", brand="Pampers", category="baby", buying_price=900, selling_price=1350, quantity=30, reorder_level=10, supplier_id=4),
        Product(name="Baby Wipes", brand="WaterWipes", category="baby", buying_price=350, selling_price=550, quantity=45, reorder_level=15, supplier_id=4),
        Product(name="Baby Oil", brand="Johnson's", category="baby", buying_price=220, selling_price=400, quantity=40, reorder_level=12, supplier_id=4),
    ]
    db.session.add_all(products)
    db.session.commit()
    
    # Add Customers
    customers = [
        Customer(name="Grace Atieno", phone="0712345678", email="grace@gmail.com", skin_type="dry", hair_type="normal", products_bought="Moisturizing Lotion, Lipstick", notes="Prefers natural products"),
        Customer(name="Faith Wanjiku", phone="0723456789", email="faith@yahoo.com", skin_type="oily", hair_type="dry", products_bought="Face Wash, Hair Oil", notes="Buy often"),
        Customer(name="Joyce Akinyi", phone="0734567890", email="joyce@gmail.com", skin_type="combination", hair_type="normal", products_bought="Shampoo, Foundation", notes=""),
        Customer(name="Mary Nyong'o", phone="0745678901", email="mary@email.com", skin_type="sensitive", hair_type="dry", products_bought="Hypoallergenic products", notes="Allergic to fragrances"),
        Customer(name="Sarah Kemunto", phone="0756789012", email="sarah@gmail.com", skin_type="normal", hair_type="oily", products_bought="Hair Spray, Blush", notes=""),
    ]
    db.session.add_all(customers)
    db.session.commit()
    
    # Add Sample Expenses
    today = datetime.now().date()
    expenses = [
        Expense(date=today - timedelta(days=1), category="rent", description="Monthly Shop Rent", amount=25000),
        Expense(date=today - timedelta(days=2), category="transport", description="Transport for stock pickup", amount=2500),
        Expense(date=today - timedelta(days=3), category="utilities", description="Electricity Bill", amount=4500),
        Expense(date=today - timedelta(days=5), category="stock_purchase", description="Stock from Beauty Supplies", amount=35000),
        Expense(date=today - timedelta(days=7), category="other", description="Shop Maintenance", amount=3000),
    ]
    db.session.add_all(expenses)
    db.session.commit()
    
    print("Cosmetic shop sample data added successfully!")
    print(f"- {len(suppliers)} suppliers")
    print(f"- {len(products)} products")
    print(f"- {len(customers)} customers")
    print(f"- {len(expenses)} expenses")
