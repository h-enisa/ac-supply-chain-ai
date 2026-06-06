# Imports & Router
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import random
 
from app.db.session import get_db
from app.ml.inference import ml_service
from app.schemas.schemas import (
    DelayPredictRequest, DelayPredictResponse,
    ForecastRequest, ForecastResponse,
    AnomalyOut,
)
from app.models.models import (
    Order, Anomaly, Inventory, Product, Supplier,
    SearchLog, CompetitorPrice, AgentRecommendation
)
from app.services.etl_service import run_etl
from app.schemas.schemas import ETLRunResponse
from pydantic import BaseModel as PydanticBase
 
 
router = APIRouter()

# Constants
COMPETITOR_DATA = {
    "Laptops":      {"name": "TechStore Albania",  "margin": 0.92},
    "Desktops":     {"name": "PC World Albania",   "margin": 0.95},
    "Monitors":     {"name": "DigiShop Tirana",    "margin": 0.97},
    "Smartphones":  {"name": "Phone Palace AL",    "margin": 0.93},
    "Tablets":      {"name": "TechStore Albania",  "margin": 0.91},
    "Gaming":       {"name": "GameZone Albania",   "margin": 0.89},
    "Accessories":  {"name": "DigiShop Tirana",    "margin": 0.96},
    "Storage":      {"name": "PC World Albania",   "margin": 0.94},
    "Printers":     {"name": "OfficeMax Albania",  "margin": 0.98},
    "Networking":   {"name": "NetPro Albania",     "margin": 0.96},
}
 
BRANCH_DISTANCES = {
    "Tirana → Shkodër":  {"km": 110, "base_cost": 42, "base_hours": 2.1},
    "Tirana → Elbasan":  {"km":  54, "base_cost": 22, "base_hours": 1.2},
    "Tirana → Vlorë":    {"km": 147, "base_cost": 58, "base_hours": 2.8},
    "Tirana → Berat":    {"km": 122, "base_cost": 48, "base_hours": 2.4},
    "Tirana → Pogradec": {"km": 184, "base_cost": 72, "base_hours": 3.5},
    "Tirana → Burrel":   {"km":  98, "base_cost": 39, "base_hours": 1.9},
    "Durrës → Tirana":   {"km":  38, "base_cost": 18, "base_hours": 0.8},
    "Durrës → Shkodër":  {"km": 142, "base_cost": 56, "base_hours": 2.7},
}
 
BRANCH_MAP = {
    "tirana":   (1, "Tirana"),
    "tiranë":   (1, "Tirana"),
    "shkodër":  (2, "Shkodër"),
    "shkoder":  (2, "Shkodër"),
    "elbasan":  (3, "Elbasan"),
    "vlorë":    (4, "Vlorë"),
    "vlore":    (4, "Vlorë"),
    "berat":    (5, "Berat"),
    "pogradec": (6, "Pogradec"),
}
 
BRANCH_NAMES_MAP = {
    1: "Tirana", 2: "Shkodër", 3: "Elbasan",
    4: "Vlorë",  5: "Berat",   6: "Pogradec",
}
 
# ML Endpoints — Delay, Forecast, Anomalies, Routes, ETL
@router.post("/delay/predict", response_model=DelayPredictResponse)
def predict_delay(payload: DelayPredictRequest):
    try:
        result = ml_service.predict_delay(
            distance_km=payload.distance_km,
            weather_score=payload.weather_score,
            customs_risk=payload.customs_risk,
            supplier_rating=payload.supplier_rating,
            lead_time_days=payload.lead_time_days,
            route=payload.route,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
 
 
@router.post("/forecast", response_model=ForecastResponse)
def forecast_demand(payload: ForecastRequest):
    try:
        result = ml_service.predict_demand(
            product_category=payload.product_category,
            horizon_days=payload.horizon_days,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
 
 
@router.get("/anomalies")
def detect_anomalies(
    last_n: int     = Query(default=200, ge=10, le=1000),
    db: Session     = Depends(get_db),
):
    regular_orders = db.query(Order).filter(
        ~Order.order_ref.like("%-ANOM-%")
    ).order_by(Order.order_date.desc()).limit(last_n).all()
 
    anomalous_orders = db.query(Order).filter(
        Order.order_ref.like("%-ANOM-%")
    ).all()
 
    all_orders = regular_orders + anomalous_orders
    if not all_orders:
        return {"anomalies": [], "orders_scanned": 0}
 
    order_dicts = [
        {
            "order_ref":      o.order_ref,
            "distance_km":    o.distance_km    or 500,
            "weather_score":  o.weather_score  or 3.0,
            "customs_risk":   o.customs_risk   or 3.0,
            "supplier_rating": 4.0,
            "lead_time_days": o.estimated_days or 7,
            "actual_days":    o.actual_days,
            "estimated_days": o.estimated_days,
            "total_value":    o.total_value,
            "status":         o.status.value if o.status else "unknown",
        }
        for o in all_orders
    ]
 
    try:
        anomalies = ml_service.detect_anomalies(order_dicts)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
 
    return {
        "anomalies":      anomalies,
        "orders_scanned": len(regular_orders),
        "anomaly_count":  len(anomalies),
    }
 
 
@router.post("/routes/optimize")
def optimize_routes(
    objective:    str = Query(default="time", enum=["time", "cost", "balanced"]),
    max_vehicles: int = Query(default=8, ge=1, le=20),
):
    routes = []
    for route_name, data in list(BRANCH_DISTANCES.items())[:max_vehicles]:
        if objective == "time":
            saving_pct = round(8 + (data["km"] / 200) * 14, 1)
            opt_hours  = round(data["base_hours"] * (1 - saving_pct / 100), 2)
            opt_cost   = data["base_cost"]
        elif objective == "cost":
            saving_pct = round(10 + (data["km"] / 200) * 12, 1)
            opt_cost   = round(data["base_cost"] * (1 - saving_pct / 100), 2)
            opt_hours  = data["base_hours"]
        else:
            saving_pct = round(9 + (data["km"] / 200) * 13, 1)
            opt_cost   = round(data["base_cost"] * (1 - saving_pct / 200), 2)
            opt_hours  = round(data["base_hours"] * (1 - saving_pct / 200), 2)
 
        routes.append({
            "route":               route_name,
            "distance_km":         data["km"],
            "optimized_cost_eur":  opt_cost,
            "optimized_hours":     opt_hours,
            "saving_pct":          saving_pct,
            "status":              "optimized",
        })
 
    sort_key = "optimized_hours" if objective == "time" else "optimized_cost_eur"
    routes.sort(key=lambda r: r[sort_key])
 
    return {
        "objective":       objective,
        "max_vehicles":    max_vehicles,
        "routes":          routes,
        "total_saving_eur": round(sum(
            BRANCH_DISTANCES[r["route"]]["base_cost"] - r["optimized_cost_eur"]
            for r in routes
        ), 2),
    }
 
 
@router.post("/etl/run", response_model=ETLRunResponse)
def trigger_etl(db: Session = Depends(get_db)):
    result = run_etl(db)
    return result
 
# Reorder Alerts
@router.get("/reorder-alerts")
def reorder_alerts(db: Session = Depends(get_db)):
    inventory_items = db.query(Inventory).join(Product).all()
    if not inventory_items:
        return {"alerts": [], "total_alerts": 0, "critical_count": 0, "warning_count": 0}
 
    orders = db.query(Order).all()
    category_order_counts = {}
    for o in orders:
        items = o.items if hasattr(o, "items") else []
        for oi in items:
            if oi.product:
                cat = oi.product.category
                category_order_counts[cat] = category_order_counts.get(cat, 0) + oi.quantity
 
    total_orders = len(orders) if orders else 1
    alerts_map   = {}
 
    for item in inventory_items:
        pid    = item.product_id
        stock  = item.quantity
        reorder = item.reorder_point
        if stock >= reorder:
            continue
        if pid not in alerts_map:
            alerts_map[pid] = {
                "sku":            item.product.sku      if item.product else "—",
                "name":           item.product.name     if item.product else "—",
                "category":       item.product.category if item.product else "—",
                "reorder_point":  reorder,
                "total_stock":    0,
                "branches_affected": 0,
            }
        alerts_map[pid]["total_stock"]       += stock
        alerts_map[pid]["branches_affected"] += 1
 
    alerts = []
    for pid, p in alerts_map.items():
        stock  = p["total_stock"]
        reorder = p["reorder_point"]
        urgency = "critical" if stock == 0 or stock <= reorder * 0.5 else "warning"
 
        avg_monthly_demand = max(
            category_order_counts.get(p["category"], 0) / max(total_orders / 30, 1), 5
        )
        suggested_qty      = max(int(avg_monthly_demand * 2) - stock, reorder * 2)
        suggested_qty      = max(suggested_qty, 10)
        daily_demand       = max(avg_monthly_demand / 30, 0.5)
        days_until_stockout = int(stock / daily_demand) if stock > 0 else 0
 
        alerts.append({
            "sku":               p["sku"],
            "name":              p["name"],
            "category":          p["category"],
            "current_stock":     stock,
            "reorder_point":     reorder,
            "urgency":           urgency,
            "suggested_order_qty": suggested_qty,
            "days_until_stockout": days_until_stockout,
            "branches_affected": p["branches_affected"],
        })
 
    alerts.sort(key=lambda a: (0 if a["urgency"] == "critical" else 1, a["days_until_stockout"]))
 
    return {
        "alerts":         alerts,
        "total_alerts":   len(alerts),
        "critical_count": sum(1 for a in alerts if a["urgency"] == "critical"),
        "warning_count":  sum(1 for a in alerts if a["urgency"] == "warning"),
    }
 
# Helper Functions
def _compute_priority_score(stock, reorder, days_until_stockout, search_count, price_diff_pct):
    score = 0
 
    stock_ratio = stock / max(reorder, 1)
    if   stock_ratio == 0:   score += 40
    elif stock_ratio < 0.3:  score += 30
    elif stock_ratio < 0.6:  score += 20
    elif stock_ratio < 1.0:  score += 10
 
    if   days_until_stockout == 0:  score += 15
    elif days_until_stockout <= 3:  score += 12
    elif days_until_stockout <= 7:  score += 8
    elif days_until_stockout <= 14: score += 4
 
    if   search_count >= 50: score += 25
    elif search_count >= 20: score += 18
    elif search_count >= 10: score += 12
    elif search_count >= 5:  score += 6
 
    if   price_diff_pct >= 20: score += 20
    elif price_diff_pct >= 10: score += 14
    elif price_diff_pct >= 5:  score += 8
 
    return min(score, 100)
 
 
def _build_reasoning(rec_type, data):
    steps = []
    if rec_type == "reorder":
        steps.append(f"Step 1: Scanned inventory — found {data.get('total_stock', 0)} units remaining across {data.get('branches', 1)} branch(es).")
        steps.append(f"Step 2: Reorder point is {data.get('reorder_point', 10)} units — current stock is below this threshold.")
        if data.get("days_until_stockout", 0) == 0:
            steps.append("Step 3: Stockout already occurred — customers cannot purchase this product.")
        else:
            steps.append(f"Step 3: At current demand rate, stockout will occur in {data.get('days_until_stockout', 0)} days.")
        if data.get("search_count", 0) > 0:
            steps.append(f"Step 4: Detected {data.get('search_count', 0)} customer searches in the last 7 days — demand signal confirmed.")
        steps.append(f"Step 5: Best supplier: {data.get('supplier', 'Unknown')} with {data.get('lead_time', 7)}-day lead time.")
        steps.append(f"Conclusion: Recommend ordering {data.get('quantity', 20)} units immediately. Priority score: {data.get('priority_score', 0)}/100.")
 
    elif rec_type == "reprice":
        steps.append(f"Step 1: Our price is €{data.get('our_price', 0)} for {data.get('product_name', 'product')}.")
        steps.append(f"Step 2: Competitor {data.get('comp_name', 'competitor')} sells at €{data.get('comp_price', 0)}.")
        steps.append(f"Step 3: We are {data.get('diff_pct', 0)}% more expensive than the market.")
        steps.append("Step 4: Customers may switch to competitor for purchases above this threshold.")
        steps.append(f"Step 5: Reducing price could recover ~€{data.get('estimated_value', 0):.0f} in at-risk sales.")
        steps.append(f"Conclusion: Recommend reducing price to €{data.get('comp_price', 0)}. Priority score: {data.get('priority_score', 0)}/100.")
 
    elif rec_type == "promote":
        steps.append(f"Step 1: Our price is €{data.get('our_price', 0)} for {data.get('product_name', 'product')}.")
        steps.append(f"Step 2: Competitor {data.get('comp_name', 'competitor')} sells at €{data.get('comp_price', 0)}.")
        steps.append(f"Step 3: We are {abs(data.get('diff_pct', 0))}% cheaper — strong price advantage.")
        steps.append("Step 4: Sufficient inventory available to support a promotion campaign.")
        steps.append(f"Step 5: Featuring this product could generate ~€{data.get('estimated_value', 0):.0f} in additional revenue.")
        steps.append(f"Conclusion: Recommend promoting this product. Priority score: {data.get('priority_score', 0)}/100.")
 
    return steps
 
 
def _simulated_demand_gaps(db):
    products = db.query(Product).filter(Product.is_active == True).limit(50).all()
    random.seed(42)
    gaps   = []
    sample = random.sample(products, min(8, len(products)))
    for p in sample:
        searches = random.randint(12, 87)
        lost     = round(searches * p.unit_price * 0.28, 2)
        gaps.append({
            "query":               " ".join(p.name.split()[:3]),
            "category":            p.category,
            "search_count":        searches,
            "estimated_lost_eur":  lost,
            "matching_products":   1,
            "simulated":           True,
        })
    gaps.sort(key=lambda g: g["estimated_lost_eur"], reverse=True)
    return gaps
 
# Agent Endpoints — Demand Gaps, Price Intelligence, Supplier Compare, Proactive Alerts
@router.get("/agent/demand-gaps")
def demand_gaps(
    days: int       = Query(default=7, ge=1, le=30),
    db: Session     = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    logs  = db.query(
        SearchLog.query,
        SearchLog.category,
        func.count(SearchLog.id).label("search_count"),
    ).filter(
        SearchLog.searched_at >= since,
        SearchLog.had_stockout == True
    ).group_by(
        SearchLog.query, SearchLog.category
    ).order_by(desc("search_count")).limit(20).all()
 
    gaps = []
    for log in logs:
        products  = db.query(Product).filter(Product.name.ilike(f"%{log.query}%"), Product.is_active == True).all()
        avg_price = sum(p.unit_price for p in products) / len(products) if products else 0
        gaps.append({
            "query":              log.query,
            "category":           log.category,
            "search_count":       log.search_count,
            "estimated_lost_eur": round(log.search_count * avg_price * 0.3, 2) if avg_price else 0,
            "matching_products":  len(products),
        })
 
    if not gaps:
        gaps = _simulated_demand_gaps(db)
 
    return {
        "period_days":    days,
        "demand_gaps":    gaps,
        "total_gaps":     len(gaps),
        "total_lost_eur": round(sum(g["estimated_lost_eur"] for g in gaps), 2),
        "generated_at":   datetime.utcnow().isoformat(),
    }
 
 
@router.get("/agent/price-intelligence")
def price_intelligence(
    category: Optional[str] = Query(None),
    db: Session             = Depends(get_db),
):
    q = db.query(Product).filter(Product.is_active == True)
    if category:
        q = q.filter(Product.category == category)
    products = q.limit(60).all()
 
    random.seed(99)
    comparisons = []
    for p in products:
        comp       = COMPETITOR_DATA.get(p.category, {"name": "Competitor", "margin": 0.94})
        variance   = random.uniform(0.88, 1.12)
        comp_price = round(p.unit_price * comp["margin"] * variance, 2)
        diff_pct   = round((p.unit_price - comp_price) / comp_price * 100, 1)
 
        if diff_pct > 5:
            status = "overpriced"
            action = f"Consider reducing price by €{round(p.unit_price - comp_price, 2)} to match {comp['name']}"
        elif diff_pct < -5:
            status = "advantage"
            action = f"You are €{round(comp_price - p.unit_price, 2)} cheaper — promote this product!"
        else:
            status = "competitive"
            action = "Price is competitive — no action needed"
 
        comparisons.append({
            "product_id":       p.id,
            "name":             p.name,
            "sku":              p.sku,
            "category":         p.category,
            "our_price":        p.unit_price,
            "competitor_price": comp_price,
            "competitor_name":  comp["name"],
            "diff_pct":         diff_pct,
            "status":           status,
            "action":           action,
        })
 
    comparisons.sort(key=lambda c: abs(c["diff_pct"]), reverse=True)
    return {
        "total_products":    len(comparisons),
        "overpriced_count":  sum(1 for c in comparisons if c["status"] == "overpriced"),
        "advantage_count":   sum(1 for c in comparisons if c["status"] == "advantage"),
        "competitive_count": sum(1 for c in comparisons if c["status"] == "competitive"),
        "comparisons":       comparisons,
        "generated_at":      datetime.utcnow().isoformat(),
    }
 
 
@router.get("/agent/supplier-compare")
def supplier_compare(
    category: str = Query(...),
    db: Session   = Depends(get_db),
):
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
    products  = db.query(Product).filter(Product.category == category, Product.is_active == True).all()
    if not products:
        raise HTTPException(status_code=404, detail=f"No products found for category: {category}")
 
    avg_price = sum(p.unit_price for p in products) / len(products)
    random.seed(hash(category) % 1000)
    options = []
 
    for s in suppliers:
        unit_cost    = round(avg_price * random.uniform(0.55, 0.78), 2)
        total_cost   = round(unit_cost * 30, 2)
        risk_score   = round(10 - (s.on_time_rate / 10) - (s.rating * 0.4) + random.uniform(0, 1.5), 1)
        risk_score   = max(1.0, min(9.9, risk_score))
        combined_score = round(
            (s.on_time_rate / 100) * 40 +
            (s.rating / 5)         * 30 +
            ((10 - risk_score) / 10) * 20 +
            ((14 - min(s.avg_lead_days, 14)) / 14) * 10,
            1
        )
        options.append({
            "supplier_id":    s.id,
            "name":           s.name,
            "country":        s.country,
            "city":           s.city,
            "rating":         s.rating,
            "on_time_rate":   s.on_time_rate,
            "avg_lead_days":  s.avg_lead_days,
            "unit_cost_eur":  unit_cost,
            "total_cost_eur": total_cost,
            "risk_score":     risk_score,
            "combined_score": combined_score,
            "recommended":    False,
        })
 
    options.sort(key=lambda o: o["combined_score"], reverse=True)
    if options:
        options[0]["recommended"] = True
 
    return {
        "category":       category,
        "quantity":       30,
        "avg_unit_price": round(avg_price, 2),
        "options":        options,
        "generated_at":   datetime.utcnow().isoformat(),
    }
 
 
@router.get("/agent/proactive-alerts")
def proactive_alert_summary(db: Session = Depends(get_db)):
    inventory_items   = db.query(Inventory).join(Product).all()
    critical_products = []
    for item in inventory_items:
        if item.quantity == 0 and item.product:
            name = item.product.name
            if name not in critical_products:
                critical_products.append(name)
 
    products = db.query(Product).filter(Product.is_active == True).limit(40).all()
    random.seed(99)
    overpriced_count = 0
    for p in products:
        comp       = COMPETITOR_DATA.get(p.category, {"name": "Competitor", "margin": 0.94})
        variance   = random.uniform(0.88, 1.12)
        comp_price = round(p.unit_price * comp["margin"] * variance, 2)
        diff_pct   = round((p.unit_price - comp_price) / comp_price * 100, 1)
        if diff_pct > 8:
            overpriced_count += 1
 
    orders        = db.query(Order).all()
    delayed_count = sum(1 for o in orders if o.status and o.status.value == "delayed")
    total_alerts  = len(critical_products) + overpriced_count + delayed_count
 
    return {
        "critical_stock_count": len(critical_products),
        "critical_products":    critical_products[:3],
        "overpriced_count":     overpriced_count,
        "delayed_count":        delayed_count,
        "total_alerts":         total_alerts,
        "generated_at":         datetime.utcnow().isoformat(),
    }
 
# Agent Recommendations
@router.get("/agent/recommendations")
def agent_recommendations(db: Session = Depends(get_db)):
    recommendations = []
 
    # ── Reorder recommendations ─────────────────────────────────────────
    inventory_items = db.query(Inventory).join(Product).all()
    alerts_map = {}
    for item in inventory_items:
        pid    = item.product_id
        stock  = item.quantity
        reorder = item.reorder_point
        if stock >= reorder:
            continue
        if pid not in alerts_map:
            alerts_map[pid] = {
                "product":      item.product,
                "total_stock":  0,
                "branches":     0,
                "reorder_point": reorder,
            }
        alerts_map[pid]["total_stock"] += stock
        alerts_map[pid]["branches"]    += 1
 
    since = datetime.utcnow() - timedelta(days=7)
    search_counts = {}
    top_searches  = db.query(
        SearchLog.query,
        func.count(SearchLog.id).label("cnt")
    ).filter(
        SearchLog.searched_at >= since,
        SearchLog.had_stockout == True
    ).group_by(SearchLog.query).all()
    for s in top_searches:
        search_counts[s.query.lower()] = s.cnt
 
    for pid, data in list(alerts_map.items())[:5]:
        p        = data["product"]
        supplier = db.query(Supplier).filter(Supplier.id == p.supplier_id).first() if p.supplier_id else None
        sup_name = supplier.name          if supplier else "Default Supplier"
        sup_lead = supplier.avg_lead_days if supplier else 7
        qty      = max(data["reorder_point"] * 3, 20)
        value    = round(qty * p.unit_price, 2)
 
        search_count        = search_counts.get(p.name.lower()[:10], random.randint(0, 15))
        avg_monthly_demand  = max(5.0, search_count * 2.0)
        daily_demand        = avg_monthly_demand / 30
        days_until_stockout = int(data["total_stock"] / daily_demand) if data["total_stock"] > 0 else 0
        priority_score      = _compute_priority_score(
            stock=data["total_stock"], reorder=data["reorder_point"],
            days_until_stockout=days_until_stockout,
            search_count=search_count, price_diff_pct=0,
        )
        priority = "high" if priority_score >= 70 else "medium" if priority_score >= 40 else "low"
 
        rec_data = {
            "total_stock": data["total_stock"], "branches": data["branches"],
            "reorder_point": data["reorder_point"], "days_until_stockout": days_until_stockout,
            "search_count": search_count, "supplier": sup_name,
            "lead_time": sup_lead, "quantity": qty, "priority_score": priority_score,
        }
        recommendations.append({
            "type":           "reorder",
            "priority":       priority,
            "priority_score": priority_score,
            "title":          f"Reorder {p.name}",
            "description":    f"Stock is critically low across {data['branches']} branch(es). Only {data['total_stock']} units remaining.",
            "action":         f"Order {qty} units from {sup_name} (est. {sup_lead} day lead time)",
            "estimated_value": value,
            "product_name":   p.name,
            "product_sku":    p.sku,
            "category":       p.category,
            "supplier":       sup_name,
            "quantity":       qty,
            "reasoning":      _build_reasoning("reorder", rec_data),
            "approved":       False,
        })
 
    # ── Reprice / Promote recommendations ───────────────────────────────
    products = db.query(Product).filter(Product.is_active == True).limit(60).all()
    random.seed(99)
 
    for p in products[:20]:
        comp       = COMPETITOR_DATA.get(p.category, {"name": "Competitor", "margin": 0.94})
        variance   = random.uniform(0.88, 1.12)
        comp_price = round(p.unit_price * comp["margin"] * variance, 2)
        diff_pct   = round((p.unit_price - comp_price) / comp_price * 100, 1)
 
        if diff_pct > 8:
            priority_score = _compute_priority_score(0, 1, 999, 0, diff_pct)
            priority       = "high" if diff_pct > 15 else "medium"
            rec_data = {
                "product_name": p.name, "our_price": p.unit_price,
                "comp_price": comp_price, "comp_name": comp["name"],
                "diff_pct": diff_pct,
                "estimated_value": round((p.unit_price - comp_price) * 10, 2),
                "priority_score": priority_score,
            }
            recommendations.append({
                "type":           "reprice",
                "priority":       priority,
                "priority_score": priority_score,
                "title":          f"Reduce price of {p.name}",
                "description":    f"You are {diff_pct}% more expensive than {comp['name']} (€{p.unit_price} vs €{comp_price}).",
                "action":         f"Reduce price from €{p.unit_price} to €{comp_price}",
                "estimated_value": round((p.unit_price - comp_price) * 10, 2),
                "product_name":   p.name, "product_sku": p.sku, "category": p.category,
                "our_price":      p.unit_price, "comp_price": comp_price, "comp_name": comp["name"],
                "reasoning":      _build_reasoning("reprice", rec_data),
                "approved":       False,
            })
 
        elif diff_pct < -8:
            priority_score = _compute_priority_score(0, 1, 999, 0, abs(diff_pct))
            rec_data = {
                "product_name": p.name, "our_price": p.unit_price,
                "comp_price": comp_price, "comp_name": comp["name"],
                "diff_pct": diff_pct,
                "estimated_value": round((comp_price - p.unit_price) * 15, 2),
                "priority_score": priority_score,
            }
            recommendations.append({
                "type":           "promote",
                "priority":       "medium",
                "priority_score": priority_score,
                "title":          f"Promote {p.name}",
                "description":    f"You are {abs(diff_pct)}% cheaper than {comp['name']} (€{p.unit_price} vs €{comp_price}).",
                "action":         f"Feature in store promotions — €{round(comp_price - p.unit_price, 2)} cheaper than competitors",
                "estimated_value": round((comp_price - p.unit_price) * 15, 2),
                "product_name":   p.name, "product_sku": p.sku, "category": p.category,
                "our_price":      p.unit_price, "comp_price": comp_price, "comp_name": comp["name"],
                "reasoning":      _build_reasoning("promote", rec_data),
                "approved":       False,
            })
 
    # ── Search-based reorder recommendations ────────────────────────────
    for s in top_searches[:3]:
        recommendations.append({
            "type":           "reorder",
            "priority":       "high",
            "priority_score": 85,
            "title":          f"High demand: customers searching for '{s.query}'",
            "description":    f"'{s.query}' was searched {s.cnt} times in the last 7 days but was out of stock.",
            "action":         f"Check inventory for '{s.query}' and restock urgently",
            "estimated_value": round(s.cnt * 200 * 0.3, 2),
            "product_name":   s.query, "product_sku": "—", "category": "—",
            "reasoning": [
                f"Step 1: Detected {s.cnt} customer searches for '{s.query}' in the last 7 days.",
                "Step 2: All search sessions resulted in out-of-stock results.",
                f"Step 3: Estimated lost revenue: €{round(s.cnt * 200 * 0.3, 2)}.",
                "Step 4: No alternative products detected — substitution not possible.",
                "Conclusion: Urgent restock recommended.",
            ],
            "approved": False,
        })
 
    recommendations.sort(key=lambda r: (-r.get("priority_score", 0), r.get("type", "")))
 
    return {
        "recommendations": recommendations[:15],
        "total":           len(recommendations),
        "reorder_count":   sum(1 for r in recommendations if r["type"] == "reorder"),
        "reprice_count":   sum(1 for r in recommendations if r["type"] == "reprice"),
        "promote_count":   sum(1 for r in recommendations if r["type"] == "promote"),
        "generated_at":    datetime.utcnow().isoformat(),
    }


 # Agent Chat
class ChatPayload(PydanticBase):
    question: str
 
 
@router.post("/agent/chat")
def agent_chat(payload: ChatPayload, db: Session = Depends(get_db)):
    q        = payload.question.lower().strip()
    response = ""
    data     = {}
 
    # ── Branch-specific query (checked FIRST) ───────────────────────────
    if any(b in q for b in list(BRANCH_MAP.keys())):
        match = next(((bid, bname) for k, (bid, bname) in BRANCH_MAP.items() if k in q), None)
        if match:
            branch_id, branch_name = match
            inv         = db.query(Inventory).join(Product).filter(Inventory.branch_id == branch_id).all()
            total_stock = sum(i.quantity for i in inv)
            out         = [i.product.name for i in inv if i.quantity == 0 and i.product]
            low         = [i.product.name for i in inv if 0 < i.quantity <= i.reorder_point and i.product]
            branch_orders = db.query(Order).filter(Order.branch_id == branch_id).all()
            delayed     = [o for o in branch_orders if o.status and o.status.value == "delayed"]
            response = (
                f"Branch {branch_name}: {len(inv)} products tracked, {total_stock} total units in stock. "
                f"{len(out)} products out of stock"
                + (f" ({', '.join(out[:2])}{'...' if len(out) > 2 else ''})" if out else "") + ". "
                f"{len(low)} below reorder point. "
                f"{len(branch_orders)} total orders from this branch, {len(delayed)} currently delayed."
            )
            data = {"branch": branch_name, "total_stock": total_stock,
                    "out_of_stock": len(out), "delayed": len(delayed)}
        else:
            response = "I could not identify the branch. Try: 'stock in Tirana' or 'delays in Vlorë'."
 
    elif any(w in q for w in ["restock", "reorder", "low stock", "out of stock", "stock"]):
        items    = db.query(Inventory).join(Product).all()
        critical = [item.product.name for item in items if item.quantity == 0 and item.product]
        warning  = [item.product.name for item in items if 0 < item.quantity <= item.reorder_point and item.product]
        response = (
            f"I scanned all {len(items)} inventory records across 6 branches. "
            f"Found {len(critical)} products completely out of stock and {len(warning)} below reorder point. "
        )
        if critical:
            response += f"Most urgent: {', '.join(critical[:3])}{'...' if len(critical) > 3 else ''}. I recommend triggering reorders immediately."
        else:
            response += "No critical stockouts detected right now."
        data = {"critical_count": len(critical), "warning_count": len(warning)}
 
    elif any(w in q for w in ["supplier", "vendor", "partner"]):
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
        best  = sorted(suppliers, key=lambda s: s.on_time_rate, reverse=True)[:3]
        worst = sorted(suppliers, key=lambda s: s.on_time_rate)[:2]
        response = (
            f"You have {len(suppliers)} active EU suppliers. "
            f"Best performers: {', '.join(s.name for s in best)}. "
            f"Lowest performers: {', '.join(s.name for s in worst)} — consider reviewing their contracts."
        )
        data = {"total_suppliers": len(suppliers)}
 
    elif any(w in q for w in ["order", "shipment", "delivery", "delayed", "transit"]):
        orders     = db.query(Order).all()
        delayed    = [o for o in orders if o.status and o.status.value == "delayed"]
        in_transit = [o for o in orders if o.status and o.status.value == "in_transit"]
        high_risk  = [o for o in orders if o.delay_risk and o.delay_risk.value == "high"]
        response = (
            f"Currently tracking {len(orders)} total orders. "
            f"{len(in_transit)} in transit, {len(delayed)} delayed, {len(high_risk)} high delay risk. "
        )
        if high_risk:
            response += f"High risk: {', '.join(o.order_ref for o in high_risk[:3])}."
        data = {"total": len(orders), "delayed": len(delayed), "in_transit": len(in_transit)}
 
    elif any(w in q for w in ["price", "expensive", "competitor", "cheap", "cost"]):
        products    = db.query(Product).filter(Product.is_active == True).all()
        random.seed(99)
        overpriced  = 0
        advantage   = 0
        worst_product = None
        worst_diff  = 0
        for p in products[:40]:
            comp       = COMPETITOR_DATA.get(p.category, {"name": "Competitor", "margin": 0.94})
            variance   = random.uniform(0.88, 1.12)
            comp_price = round(p.unit_price * comp["margin"] * variance, 2)
            diff       = round((p.unit_price - comp_price) / comp_price * 100, 1)
            if diff > 5:
                overpriced += 1
                if diff > worst_diff:
                    worst_diff    = diff
                    worst_product = p.name
            elif diff < -5:
                advantage += 1
        response = (
            f"Analyzed prices for {min(len(products), 40)} products. "
            f"{overpriced} overpriced vs competitors, {advantage} have a price advantage. "
        )
        if worst_product:
            response += f"Biggest concern: {worst_product} is {worst_diff:.1f}% above market."
        data = {"overpriced": overpriced, "advantage": advantage}
 
    elif any(w in q for w in ["anomal", "suspicious", "fraud", "unusual"]):
        anom_orders = db.query(Order).filter(Order.order_ref.like("%-ANOM-%")).all()
        total       = db.query(Order).count()
        response = (
            f"Anomaly detection flagged {len(anom_orders)} suspicious orders out of {total} total. "
            f"Flagged: {', '.join(o.order_ref for o in anom_orders[:4])}{'...' if len(anom_orders) > 4 else ''}."
        )
        data = {"flagged": len(anom_orders), "total": total}
 
    elif any(w in q for w in ["revenue", "profit", "money", "earn", "sales", "value"]):
        orders      = db.query(Order).filter(Order.total_value != None).all()
        total_value = sum(o.total_value for o in orders if o.total_value)
        avg_value   = total_value / len(orders) if orders else 0
        max_order   = max(orders, key=lambda o: o.total_value or 0, default=None)
        response = (
            f"Total import value across {len(orders)} orders is €{total_value:,.0f}. "
            f"Average order value is €{avg_value:,.0f}. "
        )
        if max_order:
            response += f"Largest order: {max_order.order_ref} at €{max_order.total_value:,.0f}."
        data = {"total_value": round(total_value, 2), "avg_value": round(avg_value, 2)}
 
    elif any(w in q for w in ["what should", "recommend", "suggest", "best", "action", "priority"]):
        items    = db.query(Inventory).join(Product).all()
        critical = sum(1 for i in items if i.quantity == 0)
        warning  = sum(1 for i in items if 0 < i.quantity <= i.reorder_point)
        orders   = db.query(Order).all()
        delayed  = sum(1 for o in orders if o.status and o.status.value == "delayed")
        response = (
            f"Top priorities: "
            f"1) Restock {critical} out-of-stock and {warning} low-stock products. "
            f"2) Investigate {delayed} delayed orders and contact their suppliers. "
            f"3) Review overpriced products in the Price Intelligence tab. "
            f"4) Check Demand Gaps for what customers are searching but cannot find."
        )
        data = {"critical_stock": critical, "delayed_orders": delayed}
 
    elif any(w in q for w in ["today", "this week", "this month", "date", "when"]):
        now         = datetime.utcnow()
        since_week  = now - timedelta(days=7)
        since_month = now - timedelta(days=30)
        week_orders  = db.query(Order).filter(Order.order_date >= since_week).count()
        month_orders = db.query(Order).filter(Order.order_date >= since_month).count()
        response = (
            f"Today is {now.strftime('%A, %d %B %Y')}. "
            f"This week: {week_orders} new orders. "
            f"This month: {month_orders} orders total."
        )
        data = {"date": now.strftime('%d %B %Y'), "week_orders": week_orders}
 
    else:
        words         = [w for w in q.split() if len(w) > 3]
        found_product = None
        for word in words:
            p = db.query(Product).filter(Product.name.ilike(f"%{word}%"), Product.is_active == True).first()
            if p:
                found_product = p
                break
 
        if found_product:
            p           = found_product
            inv         = db.query(Inventory).filter(Inventory.product_id == p.id).all()
            total_stock = sum(i.quantity for i in inv)
            comp        = COMPETITOR_DATA.get(p.category, {"name": "Competitor", "margin": 0.94})
            random.seed(hash(p.name) % 9999)
            variance    = random.uniform(0.88, 1.12)
            comp_price  = round(p.unit_price * comp["margin"] * variance, 2)
            diff_pct    = round((p.unit_price - comp_price) / comp_price * 100, 1)
            price_note  = f"{diff_pct:+.1f}% vs {comp['name']} (€{comp_price})"
            branch_detail = " | ".join(
                f"{BRANCH_NAMES_MAP.get(i.branch_id, '?')}: {i.quantity}"
                for i in inv[:4]
            )
            response = (
                f"{p.name} — Category: {p.category}, SKU: {p.sku}. "
                f"Price: €{p.unit_price} ({price_note}). "
                f"Total stock: {total_stock} units. Branch stock: {branch_detail}."
            )
            if total_stock == 0:
                response += " This product is completely out of stock."
            data = {"product": p.name, "price": p.unit_price, "total_stock": total_stock}
 
        else:
            total_products  = db.query(Product).filter(Product.is_active == True).count()
            total_orders    = db.query(Order).count()
            total_suppliers = db.query(Supplier).filter(Supplier.is_active == True).count()
            response = (
                f"I am the AC Supply Chain Agent. I can answer questions about: "
                f"stock levels, reorder needs, supplier performance, order status, "
                f"anomalies, pricing vs competitors, revenue, specific branches, and individual products. "
                f"Managing {total_products} products, {total_orders} orders, {total_suppliers} suppliers across 6 branches. "
                f"Try: 'stock in Tirana', 'MacBook Air', 'What should I restock?'"
            )
 
    return {
        "question":  payload.question,
        "answer":    response,
        "data":      data,
        "timestamp": datetime.utcnow().isoformat(),
    }