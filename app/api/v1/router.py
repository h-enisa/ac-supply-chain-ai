from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.api.v1.endpoints import auth, dashboard, orders, inventory, ml
router = APIRouter()
router.include_router(auth.router, prefix='/auth', tags=['auth'])
router.include_router(dashboard.router, prefix='/dashboard',
tags=['dashboard'], dependencies=[Depends(get_current_user)])
router.include_router(orders.router, prefix='/orders',
tags=['orders'], dependencies=[Depends(get_current_user)])
router.include_router(inventory.inv_router, prefix='/inventory',
tags=['inventory'], dependencies=[Depends(get_current_user)])
router.include_router(inventory.sup_router, prefix='/suppliers',
tags=['suppliers'], dependencies=[Depends(get_current_user)])
router.include_router(ml.router, prefix='/ml',
tags=['ml'], dependencies=[Depends(get_current_user)])
