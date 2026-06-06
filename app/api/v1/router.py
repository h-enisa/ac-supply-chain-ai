from fastapi import APIRouter, Depends

from app.api.v1.endpoints import dashboard, orders, ml
from app.api.v1.endpoints.inventory import inv_router, prod_router, sup_router, public_router
from app.api.v1.endpoints.auth import router as auth_router
from app.core.auth import get_current_user
from app.api.v1.endpoints import auth, dashboard, orders, inventory, ml

router = APIRouter()

router.include_router(auth.router, prefix='/auth', tags=['auth'])
router.include_router(inventory.public_router, prefix='/public', tags=['public'])
router.include_router(dashboard.router, prefix='/dashboard', tags=['dashboard'], dependencies=[Depends(get_current_user)])
router.include_router(orders.router, prefix='/orders', tags=['orders'], dependencies=[Depends(get_current_user)])
router.include_router(inventory.inv_router, prefix='/inventory', tags=['inventory'], dependencies=[Depends(get_current_user)])
router.include_router(inventory.sup_router, prefix='/suppliers', tags=['suppliers'], dependencies=[Depends(get_current_user)])
router.include_router(ml.router, prefix='/ml', tags=['ml'], dependencies=[Depends(get_current_user)])


api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(public_router, prefix="/public", tags=["Public"])


protected = {"dependencies": [Depends(get_current_user)]}

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"], **protected)
api_router.include_router(orders.router,    prefix="/orders",    tags=["Orders"],    **protected)
api_router.include_router(inv_router,       prefix="/inventory", tags=["Inventory"], **protected)
api_router.include_router(prod_router,      prefix="/products",  tags=["Products"],  **protected)
api_router.include_router(sup_router,       prefix="/suppliers", tags=["Suppliers"], **protected)
api_router.include_router(ml.router,        prefix="/ml",        tags=["AI / ML"],   **protected)
