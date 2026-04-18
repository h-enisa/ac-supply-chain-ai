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

    # =======================
# ML SCHEMAS
# =======================

class DelayPredictRequest(BaseModel):
    distance_km: float
    weather_score: float
    customs_risk: float
    supplier_rating: float
    lead_time_days: int
    route: str


class DelayPredictResponse(BaseModel):
    risk_class: str
    risk_probability: float
    confidence: float
    top_factors: Dict[str, float]
    model_info: Dict[str, float]


class ForecastRequest(BaseModel):
    product_category: str
    horizon_days: int


class ForecastResponse(BaseModel):
    category: str
    horizon_days: int
    rmse: float
    mae: float
    r2: float
    model_name: str
    forecast: List[Dict]


class AnomalyOut(BaseModel):
    order_ref: str
    anomaly_score: float
    anomaly_type: str
    description: str
    severity: str
    raw_score: float


class ETLRunResponse(BaseModel):
    status: str
    records_processed: int
    null_rate: float
    duration_seconds: float
    train_size: int
    test_size: int
    log: List[str]