from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    unit_price: float
    supplier_id: Optional[int] = None
    class Config:
        from_attributes = True

class InventoryOut(BaseModel):
    id: int
    product_id: int
    branch_id: int
    quantity: int
    reorder_point: int
    status: str
    product: Optional[ProductOut] = None
    class Config:
        from_attributes = True

class SupplierOut(BaseModel):
    id: int
    name: str
    country: str
    city: Optional[str]
    rating: float
    on_time_rate: float
    avg_lead_days: int
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    order_ref: str
    branch_id: int
    supplier_id: int
    status: str
    origin_city: Optional[str]
    origin_country: Optional[str]
    distance_km: Optional[float]
    estimated_days: Optional[int]
    actual_days: Optional[int]
    total_value: float
    delay_risk: str
    order_date: datetime
    class Config:
        from_attributes = True

class DashboardKPIs(BaseModel):
    active_orders: int
    on_time_delivery_pct: float
    inventory_value_eur: float
    avg_delivery_days: float
    total_skus: int
    low_stock_count: int
    out_of_stock_count: int
    monthly_orders: List[int]
    branch_distribution: Dict[str, int]