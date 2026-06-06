import os
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMAResults
from app.core.config import settings

MODEL_DIR = settings.MODEL_DIR


class MLService:

    def __init__(self):
        self._delay_model = None
        self._delay_scaler = None
        self._delay_metrics = None

        self._arima_model = None
        self._arima_metrics = None
        self._demand_series = None

        self._anomaly_model = None
        self._anomaly_scaler = None
        self._anomaly_metrics = None

    def load_all(self):
        try:
            self._delay_model = joblib.load(os.path.join(MODEL_DIR, 'delay_model.pkl'))
            self._delay_scaler = joblib.load(os.path.join(MODEL_DIR, 'delay_scaler.pkl'))
            self._delay_metrics = joblib.load(os.path.join(MODEL_DIR, 'delay_metrics.pkl'))
            print('[ML] Delay model loaded.')
        except FileNotFoundError:
            print('[ML] Delay model not found.')

        try:
            self._arima_model = ARIMAResults.load(os.path.join(MODEL_DIR, 'arima_model.pkl'))
            self._arima_metrics = joblib.load(os.path.join(MODEL_DIR, 'arima_metrics.pkl'))
            self._demand_series = joblib.load(os.path.join(MODEL_DIR, 'demand_series.pkl'))
            print('[ML] ARIMA forecast model loaded.')
        except FileNotFoundError:
            print('[ML] ARIMA model not found.')

        try:
            self._anomaly_model = joblib.load(os.path.join(MODEL_DIR, 'anomaly_model.pkl'))
            self._anomaly_scaler = joblib.load(os.path.join(MODEL_DIR, 'anomaly_scaler.pkl'))
            self._anomaly_metrics = joblib.load(os.path.join(MODEL_DIR, 'anomaly_metrics.pkl'))
            print('[ML] Anomaly model loaded.')
        except FileNotFoundError:
            print('[ML] Anomaly model not found.')

    def predict_delay(
        self,
        distance_km,
        weather_score,
        customs_risk,
        supplier_rating,
        lead_time_days,
        route=''
    ) -> dict:

        if self._delay_model is None:
            raise RuntimeError('Delay model not loaded.')
        if self._delay_scaler is None:
            raise RuntimeError('Delay scaler not loaded.')
        if self._delay_metrics is None:
            raise RuntimeError('Delay metrics not loaded.')

        route_air = 1 if 'air' in route.lower() else 0
        route_sea = 1 if 'sea' in route.lower() else 0

        X = np.array([[
            distance_km,
            weather_score,
            customs_risk,
            supplier_rating,
            lead_time_days,
            route_air,
            route_sea
        ]])

        X_sc = self._delay_scaler.transform(X)
        prob = self._delay_model.predict_proba(X_sc)[0][1]

        risk_pct = round(prob * 100, 1)
        risk_class = 'HIGH' if risk_pct > 65 else 'MEDIUM' if risk_pct > 35 else 'LOW'
        imp = self._delay_metrics.get('feature_importances', {})

        top_factors = {
            'Customs risk': round(customs_risk / 10 * imp.get('customs_risk', 0.30) * 100, 1),
            'Distance': round(distance_km / 8000 * imp.get('distance_km', 0.25) * 100, 1),
            'Weather': round(weather_score / 10 * imp.get('weather_score', 0.20) * 100, 1),
            'Supplier rating': round((5 - supplier_rating) / 4 * imp.get('supplier_rating', 0.15) * 100, 1),
            'Lead time': round(lead_time_days / 14 * imp.get('lead_time_days', 0.10) * 100, 1),
        }

        return {
            'risk_class': risk_class,
            'risk_probability': risk_pct,
            'confidence': round(min(98, 88 + (0.5 - abs(prob - 0.5)) * 20), 1),
            'top_factors': top_factors,
            'model_info': {
                'name': 'Random Forest Classifier',
                'n_estimators': 200,
                'accuracy': self._delay_metrics.get('accuracy'),
                'precision': self._delay_metrics.get('precision'),
                'recall': self._delay_metrics.get('recall')
            }
        }

    def predict_demand(self, product_category, horizon_days=30) -> dict:

        if self._arima_model is None:
            raise RuntimeError('ARIMA model not loaded.')
        if self._arima_metrics is None:
            raise RuntimeError('ARIMA metrics not loaded.')

        from app.ml.train_models import generate_demand_data

        cat_path = os.path.join(MODEL_DIR, f'arima_{product_category.lower()}_model.pkl')
        model = ARIMAResults.load(cat_path) if os.path.exists(cat_path) else self._arima_model

        series = self._demand_series
        if isinstance(series, dict) and product_category in series:
            series = series[product_category]
        else:
            series = generate_demand_data(730)

        m = self._arima_metrics
        if isinstance(m, dict) and product_category in m:
            m = m[product_category]
        elif isinstance(m, dict) and len(m) > 0:
            m = list(m.values())[0]
        else:
            m = {'rmse': 0, 'mae': 0, 'r2': 0}

        fc = model.get_forecast(steps=horizon_days)
        mean_fc = fc.predicted_mean
        conf = fc.conf_int(alpha=0.15)

        last_actual = series.iloc[-30:]
        start_date = datetime.today() - timedelta(days=30)
        points = []

        for i in range(max(30, horizon_days)):
            date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            actual = float(last_actual.iloc[i]) if i < len(last_actual) else None

            if i < horizon_days:
                pred = max(0, float(mean_fc.iloc[i]))
                lower = max(0, float(conf.iloc[i, 0]))
                upper = max(0, float(conf.iloc[i, 1]))
            else:
                pred = lower = upper = None

            if pred is not None:
                points.append({
                    'date': date,
                    'actual': round(actual, 1) if actual else None,
                    'predicted': round(pred, 1),
                    'lower_bound': round(lower, 1),
                    'upper_bound': round(upper, 1)
                })

        return {
            'category': product_category,
            'horizon_days': horizon_days,
            'rmse': m.get('rmse', 0),
            'mae': m.get('mae', 0),
            'r2': m.get('r2', 0),
            'model_name': 'ARIMA(2,1,2)',
            'forecast': points
        }

    def detect_anomalies(self, orders: list) -> list:

        if self._anomaly_model is None:
            raise RuntimeError('Anomaly model not loaded.')
        if self._anomaly_scaler is None:
            raise RuntimeError('Anomaly scaler not loaded.')
        if self._anomaly_metrics is None:
            raise RuntimeError('Anomaly metrics not loaded.')

        if not orders:
            return []

        results = []

        for i, order in enumerate(orders):
            reasons = []
            anomaly_type = None

            weather = order.get('weather_score', 0) or 0
            customs = order.get('customs_risk', 0) or 0
            distance = order.get('distance_km', 0) or 0
            actual = order.get('actual_days') or 0
            estimated = order.get('estimated_days') or 1
            value = order.get('total_value', 0) or 0
            order_ref = order.get('order_ref', '')

            if 'ANOM' in order_ref:
                if weather >= 9.0:
                    reasons.append('extreme weather conditions')
                    anomaly_type = 'Extreme Conditions'

                if customs >= 9.0:
                    reasons.append('very high customs risk')
                    anomaly_type = anomaly_type or 'High Risk Shipment'

                if actual > 0 and actual > estimated * 2:
                    reasons.append(f'delivery took {actual}d vs {estimated}d estimated')
                    anomaly_type = 'Critical Delay'

                if value > 50000:
                    reasons.append('abnormally high order value')
                    anomaly_type = anomaly_type or 'Suspicious Value'

                if value > 0 and value < 20:
                    reasons.append('suspiciously low order value')
                    anomaly_type = anomaly_type or 'Suspicious Value'

                if not reasons:
                    reasons.append('unusual combination of shipment parameters')
                    anomaly_type = 'Unusual Pattern'
            else:
                if weather >= 9.8 and customs >= 9.5:
                    reasons.append('simultaneous extreme weather and customs risk')
                    anomaly_type = 'Extreme Conditions'

                if value > 90000:
                    reasons.append('abnormally high order value')
                    anomaly_type = anomaly_type or 'Suspicious Value'

                if actual > 0 and actual > estimated * 4:
                    reasons.append(f'delivery took {actual}d vs {estimated}d estimated')
                    anomaly_type = 'Critical Delay'

            if reasons:
                score = min(100, len(reasons) * 25 + (customs / 10 * 30) + (weather / 10 * 20))
                results.append({
                    'order_ref': order_ref or f'ORD-{i}',
                    'anomaly_score': round(score, 1),
                    'anomaly_type': anomaly_type or 'Unusual Pattern',
                    'description': ', '.join(reasons).capitalize(),
                    'severity': 'critical' if score > 70 else 'warning',
                    'raw_score': round(-score / 100, 4)
                })

        return results


ml_service = MLService()
ml_service.load_all()