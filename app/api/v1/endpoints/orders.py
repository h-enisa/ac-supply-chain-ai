from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.models import Order, OrderStatus
from app.schemas.schemas import OrderOut
router = APIRouter()
@router.get('/', response_model=List[OrderOut], summary='Get all orders')
def get_orders(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Order)
    if status:
        try:
            q = q.filter(Order.status == OrderStatus(status))
        except ValueError:
            pass
    return q.order_by(Order.order_date.desc()).limit(100).all()