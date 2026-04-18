from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class OrderStatus(str, enum.Enum):
    processing = 'processing'
    in_transit = 'in_transit'
    delivered = 'delivered'
    delayed = 'delayed'
    cancelled = 'cancelled'

class StockStatus(str, enum.Enum):
    ok = 'ok'
    low_stock = 'low_stock'
    out_of_stock = 'out_of_stock'

class Branch(Base):
    __tablename__ = 'branches'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    orders = relationship('Order', back_populates='branch')
    inventory = relationship('Inventory', back_populates='branch')

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100))
    contact_email = Column(String(150))
    rating = Column(Float, default=4.0)
    on_time_rate = Column(Float, default=90.0)
    avg_lead_days = Column(Integer, default=7)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    orders = relationship('Order', back_populates='supplier')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    unit_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    inventory = relationship('Inventory', back_populates='product')
    order_items = relationship('OrderItem', back_populates='product')

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    quantity = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    status = Column(Enum(StockStatus), default=StockStatus.ok)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    product = relationship('Product', back_populates='inventory')
    branch = relationship('Branch', back_populates='inventory')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    order_ref = Column(String(50), unique=True, nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.processing)
    origin_city = Column(String(100))
    origin_country = Column(String(100))
    distance_km = Column(Float)
    estimated_days = Column(Integer)
    actual_days = Column(Integer, nullable=True)
    total_value = Column(Float, default=0.0)
    delay_risk = Column(String(10), default='low')
    weather_score = Column(Float, default=3.0)
    customs_risk = Column(Float, default=3.0)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    branch = relationship('Branch', back_populates='orders')
    supplier = relationship('Supplier', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

class Anomaly(Base):
    __tablename__ = 'anomalies'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    anomaly_score = Column(Float)
    severity = Column(String(20))
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

class DemandRecord(Base):
    __tablename__ = 'demand_records'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    quantity = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())