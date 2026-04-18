"""
Database Seeder
Populates the database with realistic data for American Computers Albania.
Run once after creating tables:
python -m scripts.seed_db
"""
from datetime import datetime, timedelta
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal, engine
from app.models.models import (
    Base, Branch, Supplier, Product,
    Inventory, Order, OrderItem, DemandRecord,
    OrderStatus, StockStatus
)

random.seed(42)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Branch).count() > 0:
            print('Database already seeded. Skipping.')
            return

        branches = [
            Branch(name='American Computers Tirana', city='Tirana', is_active=True),
            Branch(name='American Computers Shkoder', city='Shkoder', is_active=True),
            Branch(name='American Computers Elbasan', city='Elbasan', is_active=True),
            Branch(name='American Computers Vlore', city='Vlore', is_active=True),
            Branch(name='American Computers Berat', city='Berat', is_active=True),
            Branch(name='American Computers Pogradec', city='Pogradec', is_active=True),
        ]
        db.add_all(branches)
        db.flush()

        suppliers = [
            Supplier(name='Tech-Import EU', country='Italy', city='Milan',
                contact_email='contact@techimport.it', rating=4.7, on_time_rate=94,
                avg_lead_days=5, is_active=True),
            Supplier(name='TechDistrib GmbH', country='Germany', city='Frankfurt',
                contact_email='sales@techdistrib.de', rating=4.3, on_time_rate=89,
                avg_lead_days=7, is_active=True),
            Supplier(name='Samsung EMEA', country='Turkey', city='Istanbul',
                contact_email='emea@samsung.com', rating=4.5, on_time_rate=91,
                avg_lead_days=6, is_active=True),
            Supplier(name='Dell EMEA', country='Netherlands', city='Amsterdam',
                contact_email='emea@dell.com', rating=3.8, on_time_rate=78,
                avg_lead_days=9, is_active=True),
            Supplier(name='Apple EMEA', country='Germany', city='Dusseldorf',
                contact_email='emea@apple.com', rating=4.9, on_time_rate=95,
                avg_lead_days=4, is_active=True),
            Supplier(name='ASUS EU', country='Greece', city='Athens',
                contact_email='eu@asus.com', rating=4.0, on_time_rate=82,
                avg_lead_days=8, is_active=True),
            Supplier(name='Corsair EU', country='France', city='Lyon',
                contact_email='eu@corsair.com', rating=4.8, on_time_rate=97,
                avg_lead_days=3, is_active=True),
            Supplier(name='Lenovo EMEA', country='Hungary', city='Budapest',
                contact_email='emea@lenovo.com', rating=4.6, on_time_rate=93,
                avg_lead_days=5, is_active=True),
            Supplier(name='HP EMEA', country='Netherlands', city='Amsterdam',
                contact_email='emea@hp.com', rating=4.2, on_time_rate=87,
                avg_lead_days=6, is_active=True),
            Supplier(name='MSI Europe', country='Germany', city='Munich',
                contact_email='europe@msi.com', rating=4.4, on_time_rate=88,
                avg_lead_days=7, is_active=True),
        ]
        db.add_all(suppliers)
        db.flush()

        products = [
            Product(sku='LP-LN-001', name='Lenovo IdeaPad 3 15 AMD Ryzen 5', category='Laptops', unit_price=499, is_active=True),
            Product(sku='LP-LN-002', name='Lenovo ThinkPad E15 Gen 4 i5', category='Laptops', unit_price=749, is_active=True),
            Product(sku='LP-LN-003', name='Lenovo ThinkPad L14 Gen 3 i7', category='Laptops', unit_price=899, is_active=True),
            Product(sku='LP-LN-004', name='Lenovo IdeaPad Gaming 3 RTX 3050', category='Laptops', unit_price=799, is_active=True),
            Product(sku='LP-LN-005', name='Lenovo Yoga 7 14 2-in-1 Touch', category='Laptops', unit_price=849, is_active=True),
            Product(sku='LP-LN-006', name='Lenovo IdeaPad Slim 5 OLED i5', category='Laptops', unit_price=679, is_active=True),
            Product(sku='LP-HP-001', name='HP 255 G9 AMD Ryzen 5', category='Laptops', unit_price=449, is_active=True),
            Product(sku='LP-HP-002', name='HP ProBook 450 G9 i5', category='Laptops', unit_price=699, is_active=True),
            Product(sku='LP-HP-003', name='HP EliteBook 840 G9 i7', category='Laptops', unit_price=1099, is_active=True),
            Product(sku='LP-HP-004', name='HP Pavilion 15 i5 FHD IPS', category='Laptops', unit_price=579, is_active=True),
            Product(sku='LP-HP-005', name='HP OMEN 16 RTX 4060 Gaming', category='Laptops', unit_price=1249, is_active=True),
            Product(sku='LP-HP-006', name='HP Stream 14 Intel Celeron', category='Laptops', unit_price=299, is_active=True),
            Product(sku='LP-DL-001', name='Dell Inspiron 15 3520 i5', category='Laptops', unit_price=549, is_active=True),
            Product(sku='LP-DL-002', name='Dell Latitude 5530 i7 Business', category='Laptops', unit_price=999, is_active=True),
            Product(sku='LP-DL-003', name='Dell XPS 13 Plus i7 OLED', category='Laptops', unit_price=1499, is_active=True),
            Product(sku='LP-DL-004', name='Dell Vostro 3520 i5', category='Laptops', unit_price=599, is_active=True),
            Product(sku='LP-AS-001', name='ASUS VivoBook 15 X1502 i5', category='Laptops', unit_price=529, is_active=True),
            Product(sku='LP-AS-002', name='ASUS ROG Strix G15 RTX 4070', category='Laptops', unit_price=1349, is_active=True),
            Product(sku='LP-AS-003', name='ASUS ZenBook 14 OLED i7', category='Laptops', unit_price=999, is_active=True),
            Product(sku='LP-AS-004', name='ASUS ExpertBook B1 i5 Business', category='Laptops', unit_price=649, is_active=True),
            Product(sku='LP-AP-001', name='Apple MacBook Air M2 13 8GB', category='Laptops', unit_price=1199, is_active=True),
            Product(sku='LP-AP-002', name='Apple MacBook Air M2 13 16GB', category='Laptops', unit_price=1399, is_active=True),
            Product(sku='LP-AP-003', name='Apple MacBook Pro M3 14', category='Laptops', unit_price=1999, is_active=True),
            Product(sku='LP-MS-001', name='MSI Modern 15 i7 12th Gen', category='Laptops', unit_price=699, is_active=True),
            Product(sku='LP-MS-002', name='MSI Prestige 14 Evo i7', category='Laptops', unit_price=849, is_active=True),
            Product(sku='PC-HP-001', name='HP EliteDesk 800 G9 i5 SFF', category='Desktops', unit_price=749, is_active=True),
            Product(sku='PC-HP-002', name='HP ProDesk 400 G7 i3', category='Desktops', unit_price=499, is_active=True),
            Product(sku='PC-LN-001', name='Lenovo ThinkCentre M70q i5 Tiny', category='Desktops', unit_price=649, is_active=True),
            Product(sku='PC-LN-002', name='Lenovo IdeaCentre 5i i7 Tower', category='Desktops', unit_price=849, is_active=True),
            Product(sku='PC-DL-001', name='Dell OptiPlex 7000 i5 Micro', category='Desktops', unit_price=699, is_active=True),
            Product(sku='PC-AS-001', name='ASUS ExpertCenter D500 i5 Tower', category='Desktops', unit_price=599, is_active=True),
            Product(sku='PC-MS-001', name='MSI PRO DP21 i5 Mini PC', category='Desktops', unit_price=549, is_active=True),
            Product(sku='MN-LG-001', name='LG 24MK430H 24 FHD IPS 75Hz', category='Monitors', unit_price=129, is_active=True),
            Product(sku='MN-LG-002', name='LG UltraWide 34WN650 34 FHD IPS', category='Monitors', unit_price=299, is_active=True),
            Product(sku='MN-LG-003', name='LG 27GP850 27 QHD 165Hz Gaming', category='Monitors', unit_price=349, is_active=True),
            Product(sku='MN-SM-001', name='Samsung 27 F27T450 IPS FHD', category='Monitors', unit_price=189, is_active=True),
            Product(sku='MN-SM-002', name='Samsung Odyssey G5 27 QHD 165Hz', category='Monitors', unit_price=279, is_active=True),
            Product(sku='MN-SM-003', name='Samsung 32 ViewFinity S8 4K UHD', category='Monitors', unit_price=499, is_active=True),
            Product(sku='MN-AS-001', name='ASUS ProArt PA278QV 27 WQHD', category='Monitors', unit_price=369, is_active=True),
            Product(sku='MN-DL-001', name='Dell P2422H 24 FHD IPS', category='Monitors', unit_price=199, is_active=True),
            Product(sku='MN-HP-001', name='HP V24i FHD 24 IPS Monitor', category='Monitors', unit_price=149, is_active=True),
            Product(sku='MN-HP-002', name='HP M27fw FHD 27 IPS Frameless', category='Monitors', unit_price=219, is_active=True),
            Product(sku='MN-MS-001', name='MSI PRO MP273 27 FHD IPS', category='Monitors', unit_price=179, is_active=True),
            Product(sku='SP-SM-001', name='Samsung Galaxy A55 5G 128GB', category='Smartphones', unit_price=349, is_active=True),
            Product(sku='SP-SM-002', name='Samsung Galaxy A35 5G 128GB', category='Smartphones', unit_price=279, is_active=True),
            Product(sku='SP-SM-003', name='Samsung Galaxy S24 128GB', category='Smartphones', unit_price=799, is_active=True),
            Product(sku='SP-SM-004', name='Samsung Galaxy S24+ 256GB', category='Smartphones', unit_price=999, is_active=True),
            Product(sku='SP-SM-005', name='Samsung Galaxy A15 5G 128GB', category='Smartphones', unit_price=199, is_active=True),
            Product(sku='SP-SM-006', name='Samsung Galaxy A25 5G 128GB', category='Smartphones', unit_price=239, is_active=True),
            Product(sku='SP-AP-001', name='Apple iPhone 15 128GB', category='Smartphones', unit_price=899, is_active=True),
            Product(sku='SP-AP-002', name='Apple iPhone 15 Pro 256GB', category='Smartphones', unit_price=1199, is_active=True),
            Product(sku='SP-AP-003', name='Apple iPhone 15 Pro Max 256GB', category='Smartphones', unit_price=1399, is_active=True),
            Product(sku='SP-AP-004', name='Apple iPhone 14 128GB', category='Smartphones', unit_price=699, is_active=True),
        ]
        db.add_all(products)
        db.flush()

        stock_by_category = {
            'Laptops': [80, 35, 28, 22, 15, 10],
            'Desktops': [55, 22, 18, 14, 10, 7],
            'Monitors': [70, 30, 24, 18, 12, 8],
            'Smartphones': [150, 60, 48, 38, 25, 16],
            'Tablets': [65, 26, 20, 16, 10, 7],
            'Gaming': [75, 30, 24, 18, 12, 8],
            'Accessories': [220, 85, 68, 52, 35, 22],
            'Printers': [40, 16, 12, 9, 6, 4],
            'Networking': [65, 26, 20, 16, 10, 7],
            'Storage': [130, 52, 40, 32, 20, 14],
        }

        reorder_pts = {
            'Laptops': 10, 'Desktops': 5, 'Monitors': 8,
            'Smartphones': 15, 'Tablets': 8, 'Gaming': 6,
            'Accessories': 20, 'Printers': 4, 'Networking': 6, 'Storage': 15,
        }

        for prod in products:
            base_stock = stock_by_category.get(prod.category, [10,3,2,2,1,1])
            for i, branch in enumerate(branches):
                qty = max(0, base_stock[i] + random.randint(-15, 5))
                rp = reorder_pts.get(prod.category, 8)
                if qty == 0: status = StockStatus.out_of_stock
                elif qty <= rp: status = StockStatus.low_stock
                else: status = StockStatus.ok
                db.add(Inventory(product_id=prod.id, branch_id=branch.id,
                    quantity=qty, reorder_point=rp, status=status))
        db.flush()

        supplier_routes = {
            'Tech-Import EU': ('Milan', 'Italy', 860, 3, 5),
            'TechDistrib GmbH': ('Frankfurt', 'Germany', 1820, 6, 7),
            'Samsung EMEA': ('Istanbul', 'Turkey', 1380, 4, 6),
            'Dell EMEA': ('Amsterdam', 'Netherlands', 2100, 7, 9),
            'Apple EMEA': ('Dusseldorf', 'Germany', 1820, 2, 4),
            'ASUS EU': ('Athens', 'Greece', 490, 2, 4),
            'Corsair EU': ('Lyon', 'France', 1780, 1, 3),
            'Lenovo EMEA': ('Budapest', 'Hungary', 1450, 4, 6),
            'HP EMEA': ('Amsterdam', 'Netherlands', 2100, 5, 7),
            'MSI Europe': ('Munich', 'Germany', 1700, 5, 7),
        }

        supplier_weights = [15, 12, 14, 8, 10, 8, 6, 13, 10, 4]

        statuses = ([OrderStatus.delivered]*55 + [OrderStatus.in_transit]*20 +
            [OrderStatus.processing]*15 + [OrderStatus.delayed]*8 +
            [OrderStatus.cancelled]*2)

        for i in range(500):
            sup = random.choices(suppliers, weights=supplier_weights, k=1)[0]
            route = supplier_routes[sup.name]
            branch = random.choices(branches, weights=[40,15,12,12,11,10], k=1)[0]
            status = random.choice(statuses)
            days_ago = random.randint(1, 365)
            order_dt = datetime.utcnow() - timedelta(days=days_ago)
            est_days = route[4]
            act_days = (est_days + random.randint(3,8) if status == OrderStatus.delayed
                else est_days + random.randint(-1,2) if status == OrderStatus.delivered
                else None)
            delay_risk = ('high' if status == OrderStatus.delayed else
                'medium' if status == OrderStatus.in_transit else 'low')
            chosen = random.sample(products, random.randint(1, 4))
            qtys = [random.randint(1, 10) for _ in chosen]
            total = sum(p.unit_price * q for p, q in zip(chosen, qtys))
            order = Order(
                order_ref=f'AC-{2025 if days_ago > 90 else 2026}-{str(i+1).zfill(4)}',
                branch_id=branch.id, supplier_id=sup.id,
                origin_city=route[0], origin_country=route[1],
                distance_km=round(route[2]+random.uniform(-100,100),1),
                weather_score=round(random.uniform(1.0,9.0),1),
                customs_risk=round(random.uniform(1.0,8.0),1),
                status=status, delay_risk=delay_risk,
                total_value=round(total,2), estimated_days=est_days,
                actual_days=act_days, order_date=order_dt)
            db.add(order)
            db.flush()
            for prod, qty in zip(chosen, qtys):
                db.add(OrderItem(order_id=order.id, product_id=prod.id,
                    quantity=qty, unit_price=prod.unit_price))

        db.commit()
        print('Database seeded successfully!')
        print(f' Branches: {len(branches)}')
        print(f' Suppliers: {len(suppliers)}')
        print(f' Products: {len(products)}')
        print(f' Orders: 500')

    except Exception as e:
        db.rollback()
        print(f'Seeding failed: {e}')
        raise
    finally:
        db.close()

if __name__ == '__main__':
    seed()