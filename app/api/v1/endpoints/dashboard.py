from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.models import Order, Inventory, OrderStatus, StockStatus, Product, Branch
from app.schemas.schemas import DashboardKPIs
router = APIRouter()
@router.get('/kpis', response_model=DashboardKPIs, summary='Get live dashboard KPIs')
def get_dashboard_kpis(db: Session = Depends(get_db)):
active_orders = db.query(Order).filter(
Order.status.in_([OrderStatus.processing, OrderStatus.in_transit])
).count()
total_delivered = db.query(Order).filter(Order.status == OrderStatus.delivered).count()
on_time = db.query(Order).filter(
Order.status == OrderStatus.delivered,
Order.actual_days <= Order.estimated_days
).count()
on_time_pct = round((on_time / total_delivered * 100) if total_delivered > 0 else 0, 1)
inv_value = db.query(
func.sum(Inventory.quantity * Product.unit_price)
).join(Product, Inventory.product_id == Product.id).scalar() or 0
avg_days_result = db.query(func.avg(Order.actual_days)).filter(
Order.actual_days.isnot(None)
).scalar()
avg_days = round(float(avg_days_result), 1) if avg_days_result else 0.0
low_stock = db.query(Inventory).filter(Inventory.status == StockStatus.low_stock).count()
out_stock = db.query(Inventory).filter(Inventory.status == StockStatus.out_of_stock).count()
from datetime import datetime, timedelta
now = datetime.utcnow()
monthly = []
for i in range(11, -1, -1):
month_start = (now.replace(day=1) - timedelta(days=30 * i))
month_end = (now.replace(day=1) - timedelta(days=30 * (i - 1)))
count = db.query(Order).filter(
Order.order_date >= month_start,
Order.order_date < month_end
).count()
monthly.append(count)
branches = db.query(Branch).filter(Branch.is_active == True).all()
branch_dist = {}
for b in branches:
cnt = db.query(Order).filter(Order.branch_id == b.id).count()
branch_dist[b.city] = cnt
return DashboardKPIs(
active_orders=active_orders,
on_time_delivery_pct=on_time_pct,
inventory_value_eur=float(inv_value),
avg_delivery_days=avg_days,
total_skus=db.query(Inventory).count(),
low_stock_count=low_stock,
out_of_stock_count=out_stock,
monthly_orders=monthly,
branch_distribution=branch_dist,
)