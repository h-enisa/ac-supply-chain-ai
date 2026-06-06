from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import Product, Inventory, SearchLog


public_router = APIRouter()


class SearchLogPayload(BaseModel):
    query: str
    category: Optional[str] = None
    results_count: int = 0
    had_stockout: bool = False
    had_lowstock: bool = False


@public_router.post("/log-search")
def log_search(payload: SearchLogPayload, db: Session = Depends(get_db)):
    if not payload.query or len(payload.query.strip()) < 2:
        return {"logged": False}

    log = SearchLog(
        query=payload.query.strip().lower(),
        category=payload.category,
        results_count=payload.results_count,
        had_stockout=payload.had_stockout,
        had_lowstock=payload.had_lowstock,
    )
    db.add(log)
    db.commit()
    return {"logged": True}



@public_router.get("/products")
def public_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(Product.is_active == True)

    if category:
        q = q.filter(Product.category == category)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))

    products = q.all()
    result = []

    for p in products:
        inventory = db.query(Inventory).filter(Inventory.product_id == p.id).all()
        total_stock = sum(i.quantity for i in inventory)

        if total_stock == 0:
            availability = "out_of_stock"
        elif total_stock <= sum(i.reorder_point for i in inventory):
            availability = "low_stock"
        else:
            availability = "in_stock"

        branch_stock = [
            {
                "branch_id": i.branch_id,
                "quantity": i.quantity,
                "status": (
                    "in_stock" if i.quantity > i.reorder_point
                    else ("low_stock" if i.quantity > 0 else "out_of_stock")
                ),
            }
            for i in inventory
            if i.branch_id
        ]

        result.append({
            "id":           p.id,
            "name":         p.name,
            "sku":          p.sku,
            "category":     p.category,
            "price":        p.unit_price,
            "total_stock":  total_stock,
            "availability": availability,
            "branches":     branch_stock,
        })

    return result