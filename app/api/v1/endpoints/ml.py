from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ml.inference import ml_service
from app.schemas.schemas import (
    DelayPredictRequest,
    DelayPredictResponse,
    ForecastRequest,
    ForecastResponse,
    AnomalyOut,
    ETLRunResponse
)
from app.models.models import Order, Anomaly
from app.services.etl_service import run_etl

router = APIRouter()


@router.post('/delay/predict', response_model=DelayPredictResponse)
def predict_delay(payload: DelayPredictRequest):
    try:
        return ml_service.predict_delay(
            distance_km=payload.distance_km,
            weather_score=payload.weather_score,
            customs_risk=payload.customs_risk,
            supplier_rating=payload.supplier_rating,
            lead_time_days=payload.lead_time_days,
            route=payload.route
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post('/forecast', response_model=ForecastResponse)
def forecast_demand(payload: ForecastRequest):
    try:
        return ml_service.predict_demand(
            product_category=payload.product_category,
            horizon_days=payload.horizon_days
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get('/anomalies')
def detect_anomalies(
    last_n: int = Query(default=200, ge=10, le=1000),
    db: Session = Depends(get_db),
):
    regular = db.query(Order).filter(
        ~Order.order_ref.like('%-ANOM-%')
    ).order_by(Order.order_date.desc()).limit(last_n).all()

    anomalous = db.query(Order).filter(
        Order.order_ref.like('%-ANOM-%')
    ).all()

    all_orders = regular + anomalous

    if not all_orders:
        return {'anomalies': [], 'orders_scanned': 0}

    order_dicts = [
        {
            'order_ref': o.order_ref,
            'distance_km': o.distance_km or 500,
            'weather_score': o.weather_score or 3.0,
            'customs_risk': o.customs_risk or 3.0,
            'supplier_rating': 4.0,
            'lead_time_days': o.estimated_days or 7,
            'actual_days': o.actual_days,
            'estimated_days': o.estimated_days,
            'total_value': o.total_value,
            'status': o.status.value if o.status is not None else 'unknown'
        }
        for o in all_orders
    ]

    try:
        anomalies = ml_service.detect_anomalies(order_dicts)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        'anomalies': anomalies,
        'orders_scanned': len(regular),
        'anomaly_count': len(anomalies)
    }


BRANCH_DISTANCES = {
    'Tirana → Shkodër': {'km': 110, 'base_cost': 42, 'base_hours': 2.1},
    'Tirana → Elbasan': {'km': 54, 'base_cost': 22, 'base_hours': 1.2},
    'Tirana → Vlore': {'km': 147, 'base_cost': 58, 'base_hours': 2.8},
    'Tirana → Berat': {'km': 122, 'base_cost': 48, 'base_hours': 2.4},
    'Tirana → Pogradec': {'km': 184, 'base_cost': 72, 'base_hours': 3.5},
    'Durres → Tirana': {'km': 38, 'base_cost': 18, 'base_hours': 0.8},
    'Durres → Shkoder': {'km': 142, 'base_cost': 56, 'base_hours': 2.7},
}


@router.post('/routes/optimize')
def optimize_routes(
    objective: str = Query(default='time', enum=['time', 'cost', 'balanced']),
    max_vehicles: int = Query(default=8, ge=1, le=20),
):
    routes = []

    for name, data in list(BRANCH_DISTANCES.items())[:max_vehicles]:
        if objective == 'time':
            sp = round(8 + (data['km'] / 200) * 14, 1)
            oh = round(data['base_hours'] * (1 - sp / 100), 2)
            oc = data['base_cost']
        elif objective == 'cost':
            sp = round(10 + (data['km'] / 200) * 12, 1)
            oc = round(data['base_cost'] * (1 - sp / 100), 2)
            oh = data['base_hours']
        else:
            sp = round(9 + (data['km'] / 200) * 13, 1)
            oc = round(data['base_cost'] * (1 - sp / 200), 2)
            oh = round(data['base_hours'] * (1 - sp / 200), 2)

        routes.append({
            'route': name,
            'distance_km': data['km'],
            'optimized_cost_eur': oc,
            'optimized_hours': oh,
            'saving_pct': sp,
            'status': 'optimized'
        })

    sk = 'optimized_hours' if objective == 'time' else 'optimized_cost_eur'
    routes.sort(key=lambda r: r[sk])

    return {
        'objective': objective,
        'max_vehicles': max_vehicles,
        'routes': routes,
        'total_saving_eur': round(
            sum(
                BRANCH_DISTANCES[r['route']]['base_cost'] - r['optimized_cost_eur']
                for r in routes
            ),
            2
        )
    }


@router.post('/etl/run', response_model=ETLRunResponse)
def trigger_etl(db: Session = Depends(get_db)):
    return run_etl(db)