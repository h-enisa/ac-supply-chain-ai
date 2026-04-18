from app.ml.inference import ml_service

print("\n--- DELAY ---")
print(
    ml_service.predict_delay(
        distance_km=1200,
        weather_score=7.0,
        customs_risk=3.0,
        supplier_rating=4.2,
        lead_time_days=5,
        route="air"
    )
)

print("\n--- DEMAND ---")
print(
    ml_service.predict_demand(
        product_category="laptops",
        horizon_days=5
    )
)

print("\n--- ANOMALY ---")
orders = [
    {
        "order_ref": "ANOM-001",
        "weather_score": 9.5,
        "customs_risk": 9.2,
        "distance_km": 3000,
        "actual_days": 20,
        "estimated_days": 5,
        "total_value": 80000
    }
]

print(ml_service.detect_anomalies(orders))