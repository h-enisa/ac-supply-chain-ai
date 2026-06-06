from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class DelayRisk(str, enum.Enum):
    low    = "low"
    medium = "medium"
    high   = "high"
 
 
class OrderStatus(str, enum.Enum):
    processing = "processing"
    in_transit = "in_transit"
    delivered  = "delivered"
    delayed    = "delayed"
    cancelled  = "cancelled"




class StockStatus(str, enum.Enum):
    ok = 'ok'
    low_stock = 'low_stock'
    out_of_stock = 'out_of_stock'

class Branch(Base):
    _tablename_ = "branches"
 
    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String(100), nullable=False)
    city      = Column(String(100), nullable=False)
    address   = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
 
    inventory = relationship("Inventory", back_populates="branch")
    orders    = relationship("Order", back_populates="branch")


class Supplier(Base):
    _tablename_ = "suppliers"
 
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(150), nullable=False)
    country       = Column(String(100), nullable=False)
    city          = Column(String(100), nullable=True)
    contact_email = Column(String(150), nullable=True)
    rating        = Column(Float, default=3.0)
    on_time_rate  = Column(Float, default=80.0)
    avg_lead_days = Column(Integer, default=10)
    is_active     = Column(Boolean, default=True)
 
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    _tablename_ = "products"
 
    id          = Column(Integer, primary_key=True, index=True)
    sku         = Column(String(50), unique=True, nullable=False, index=True)
    name        = Column(String(200), nullable=False)
    category    = Column(String(100), nullable=False)
    unit_price  = Column(Float, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    is_active   = Column(Boolean, default=True)
 
    supplier    = relationship("Supplier", back_populates="products")
    inventory   = relationship("Inventory", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
 


class Inventory(Base):
    _tablename_ = "inventory"
 
    id            = Column(Integer, primary_key=True, index=True)
    product_id    = Column(Integer, ForeignKey("products.id"), nullable=False)
    branch_id     = Column(Integer, ForeignKey("branches.id"), nullable=True)
    quantity      = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 
    product = relationship("Product", back_populates="inventory")
    branch  = relationship("Branch", back_populates="inventory")


class Order(Base):
    _tablename_ = "orders"
 
    id             = Column(Integer, primary_key=True, index=True)
    order_ref      = Column(String(50), unique=True, nullable=False, index=True)
    branch_id      = Column(Integer, ForeignKey("branches.id"), nullable=True)
    supplier_id    = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    status         = Column(SAEnum(OrderStatus), default=OrderStatus.processing)
    delay_risk     = Column(SAEnum(DelayRisk), default=DelayRisk.low)
    origin_city    = Column(String(100), nullable=True)
    origin_country = Column(String(100), nullable=True)
    distance_km    = Column(Float, nullable=True)
    weather_score  = Column(Float, nullable=True)
    customs_risk   = Column(Float, nullable=True)
    estimated_days = Column(Integer, nullable=True)
    actual_days    = Column(Integer, nullable=True)
    total_value    = Column(Float, nullable=True)
    order_date     = Column(DateTime(timezone=True), server_default=func.now())
 
    branch = relationship("Branch", back_populates="orders")
    items  = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    _tablename_ = "order_items"
 
    id         = Column(Integer, primary_key=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
 
    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class DemandRecord(Base):
    _tablename_ = "demand_records"
 
    id       = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    date     = Column(DateTime(timezone=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    revenue  = Column(Float, nullable=True)
 
 
class Anomaly(Base):
    _tablename_ = "anomalies"
 
    id           = Column(Integer, primary_key=True, index=True)
    order_ref    = Column(String(50), nullable=False)
    anomaly_type = Column(String(100), nullable=True)
    score        = Column(Float, nullable=True)
    detected_at  = Column(DateTime(timezone=True), server_default=func.now())
 
# -- NEW Week 6 --
 
 
class SearchLog(Base):
    _tablename_ = "search_logs"
 
    id            = Column(Integer, primary_key=True, index=True)
    query         = Column(String(200), nullable=False)
    category      = Column(String(100), nullable=True)
    results_count = Column(Integer, default=0)
    had_stockout  = Column(Boolean, default=False)
    had_lowstock  = Column(Boolean, default=False)
    searched_at   = Column(DateTime(timezone=True), server_default=func.now())
 
 
class CompetitorPrice(Base):
    _tablename_ = "competitor_prices"
 
    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey("products.id"), nullable=False)
    competitor_name  = Column(String(150), nullable=False)
    competitor_price = Column(Float, nullable=False)
    our_price        = Column(Float, nullable=False)
    price_diff_pct   = Column(Float, nullable=True)
    scraped_at       = Column(DateTime(timezone=True), server_default=func.now())
 
    product = relationship("Product")
 
 
class AgentRecommendation(Base):
    _tablename_ = "agent_recommendations"
 
    id              = Column(Integer, primary_key=True, index=True)
    type            = Column(String(50), nullable=False)
    product_id      = Column(Integer, ForeignKey("products.id"), nullable=True)
    title           = Column(String(200), nullable=False)
    description     = Column(Text, nullable=False)
    action          = Column(Text, nullable=True)
    priority        = Column(String(20), default="medium")
    estimated_value = Column(Float, nullable=True)
    is_approved     = Column(Boolean, default=False)
    is_dismissed    = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
 
    product = relationship("Product")