from fastapi import APIRouter, Depends

from app.api.v1.endpoints import dashboard, orders, ml
from app.api.v1.endpoints.inventory import inv_router, prod_router, sup_router, public_router
from app.api.v1.endpoints.auth import router as auth_router
from app.core.auth import get_current_user


api_router = APIRouter()

# Public routes (no token required)
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(public_router, prefix="/public", tags=["Public"])

# Protected routes
protected = {"dependencies": [Depends(get_current_user)]}

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"], **protected)
api_router.include_router(orders.router,    prefix="/orders",    tags=["Orders"],    **protected)
api_router.include_router(inv_router,       prefix="/inventory", tags=["Inventory"], **protected)
api_router.include_router(prod_router,      prefix="/products",  tags=["Products"],  **protected)
api_router.include_router(sup_router,       prefix="/suppliers", tags=["Suppliers"], **protected)
api_router.include_router(ml.router,        prefix="/ml",        tags=["AI / ML"],   **protected)