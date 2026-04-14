from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.session import get_db
from app.models.models import Inventory, Supplier
from app.schemas.schemas import InventoryOut, SupplierOut
inv_router = APIRouter()
sup_router = APIRouter()
prod_router = APIRouter()
@inv_router.get('/', response_model=List[InventoryOut], summary='Get all inventory')
def get_inventory(db: Session = Depends(get_db)):
return db.query(Inventory).options(joinedload(Inventory.product)).all()
@sup_router.get('/', response_model=List[SupplierOut], summary='Get all suppliers')
def get_suppliers(db: Session = Depends(get_db)):
return db.query(Supplier).filter(Supplier.is_active == True).all()