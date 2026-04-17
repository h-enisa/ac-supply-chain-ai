from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.db.session import get_db
from app.models.models import Inventory, Product, Supplier, StockStatus
from app.schemas.schemas import InventoryOut, SupplierOut
inv_router = APIRouter()
sup_router = APIRouter()
@inv_router.get('/', response_model=List[InventoryOut], summary='List inventory')
def list_inventory(
    branch_id: Optional[int] = Query(None),
    status:    Optional[str] = Query(None),
    category:  Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Inventory).join(Product).options(joinedload(Inventory.product))
    if branch_id:
        q = q.filter(Inventory.branch_id == branch_id)
    if status:
        q = q.filter(Inventory.status == status)
if category:
q = q.filter(Product.category == category)
return q.all()
@sup_router.get('/', response_model=List[SupplierOut], summary='List all suppliers')
def list_suppliers(db: Session = Depends(get_db)):
return db.query(Supplier).filter(Supplier.is_active == True).all()
@sup_router.get('/{supplier_id}', response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
if not s:
raise HTTPException(status_code=404, detail='Supplier not found')
return s
