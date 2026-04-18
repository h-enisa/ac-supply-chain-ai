import os
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)

from statsmodels.tsa.arima.model import ARIMA
from app.core.config import settings

MODEL_DIR = settings.MODEL_DIR
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_order_data(n: int = 5000) -> pd.DataFrame:
    np.random.seed(42)

    routes = [
        ('Italy', 'sea', 860),
        ('Germany', 'road', 1820),
        ('Turkey', 'road', 1380),
        ('Greece', 'road', 490),
        ('China', 'air', 7500)
    ]

    rc = np.random.choice(len(routes), n)

    df = pd.DataFrame({
        'distance_km': [routes[i][2] + np.random.normal(0, 50) for i in rc],
        'weather_score': np.random.uniform(0, 10, n),
        'customs_risk': np.random.uniform(0, 10, n),
        'supplier_rating': np.random.uniform(2.5, 5.0, n),
        'lead_time_days': np.random.randint(2, 15, n),
        'route_type_air': [1 if routes[i][1] == 'air' else 0 for i in rc],
        'route_type_sea': [1 if routes[i][1] == 'sea' else 0 for i in rc],
    })

    delay_prob = (
        df['customs_risk'] / 10 * 0.30 +
        df['distance_km'] / 8000 * 0.25 +
        df['weather_score'] / 10 * 0.20 +
        (5 - df['supplier_rating']) / 4 * 0.15 +
        df['lead_time_days'] / 14 * 0.10
    ) + np.random.normal(0, 0.05, n)

    df['delayed'] = (delay_prob > 0.38).astype(int)

    return df


def generate_demand_data(days: int = 730) -> pd.Series:
    np.random.seed(42)

    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')

    trend = np.linspace(60, 95, days)
    seasonality = 20 * np.sin(2 * np.pi * np.arange(days) / 365)
    weekly = 10 * np.sin(2 * np.pi * np.arange(days) / 7)
    noise = np.random.normal(0, 5, days)

    demand = np.maximum(0, trend + seasonality + weekly + noise).round()

    return pd.Series(demand, index=dates, name='demand')


def train_delay_model():
    print('\n[1/3] Training delay prediction model...')

    df = generate_order_data(5000)

    features = [
        'distance_km', 'weather_score', 'customs_risk',
        'supplier_rating', 'lead_time_days',
        'route_type_air', 'route_type_sea'
    ]

    X, y = df[features], df['delayed']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight='balanced'
    )

    model.fit(X_train_sc, y_train)

    y_pred = model.predict(X_test_sc)

    metrics = {
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
        'precision': round(precision_score(y_test, y_pred) * 100, 2),
        'recall': round(recall_score(y_test, y_pred) * 100, 2),
        'f1': round(f1_score(y_test, y_pred) * 100, 2),
        'features': features,
        'feature_importances': dict(
            zip(features, model.feature_importances_.round(4).tolist())
        ),
    }

    joblib.dump(model, os.path.join(MODEL_DIR, 'delay_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'delay_scaler.pkl'))
    joblib.dump(metrics, os.path.join(MODEL_DIR, 'delay_metrics.pkl'))

    print(f' Accuracy: {metrics["accuracy"]}%')

    return metrics


def train_forecast_model():
    print('\n[2/3] Training demand forecast model (ARIMA per category)...')

    categories = {
        'Laptops': {'base': 45, 'trend': 0.05, 'seasonal': 15, 'noise': 5},
        'Monitors': {'base': 30, 'trend': 0.03, 'seasonal': 10, 'noise': 4},
        'Smartphones': {'base': 60, 'trend': 0.08, 'seasonal': 25, 'noise': 8},
        'Desktops': {'base': 15, 'trend': 0.02, 'seasonal': 5, 'noise': 3},
        'Gaming': {'base': 20, 'trend': 0.06, 'seasonal': 20, 'noise': 6},
        'Accessories': {'base': 80, 'trend': 0.04, 'seasonal': 30, 'noise': 10},
        'Tablets': {'base': 25, 'trend': 0.03, 'seasonal': 12, 'noise': 4},
        'Storage': {'base': 50, 'trend': 0.02, 'seasonal': 8, 'noise': 5},
    }

    all_metrics = {}
    all_series = {}

    np.random.seed(42)
    days = 730

    for cat, params in categories.items():
        try:
            dates = pd.date_range(start='2024-01-01', periods=days, freq='D')

            trend = np.linspace(
                params['base'],
                params['base'] * (1 + params['trend'] * days),
                days
            )

            seasonal = params['seasonal'] * np.sin(2 * np.pi * np.arange(days) / 365)
            weekly = params['seasonal'] * 0.3 * np.sin(2 * np.pi * np.arange(days) / 7)
            noise = np.random.normal(0, params['noise'], days)

            demand = np.maximum(0, trend + seasonal + weekly + noise).round()

            series = pd.Series(demand, index=dates, name='demand')

            train, test = series[:-60], series[-60:]

            model = ARIMA(train, order=(2, 1, 2))
            fitted = model.fit()

            forecast = fitted.forecast(steps=60)

            rmse = round(float(np.sqrt(mean_squared_error(test, forecast))), 3)
            mae = round(float(mean_absolute_error(test, forecast)), 3)
            r2 = round(float(r2_score(test, forecast)), 3)

            metrics = {
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'order': '(2,1,2)',
                'model_name': 'ARIMA',
                'train_size': len(train),
                'test_size': len(test)
            }

            fitted.save(os.path.join(MODEL_DIR, f'arima_{cat.lower()}_model.pkl'))

            all_metrics[cat] = metrics
            all_series[cat] = series

            print(f' {cat}: RMSE={rmse} | MAE={mae} | R2={r2}')

        except Exception as e:
            print(f' {cat} failed: {e}')
            continue

    series = generate_demand_data(730)
    model = ARIMA(series[:-60], order=(2, 1, 2))
    fitted = model.fit()

    fitted.save(os.path.join(MODEL_DIR, 'arima_model.pkl'))

    joblib.dump(all_metrics, os.path.join(MODEL_DIR, 'arima_metrics.pkl'))
    joblib.dump(all_series, os.path.join(MODEL_DIR, 'demand_series.pkl'))

    return all_metrics


def train_anomaly_model():
    print('\n[3/3] Training anomaly detection model...')

    df = generate_order_data(5000)

    features = [
        'distance_km', 'weather_score',
        'customs_risk', 'supplier_rating',
        'lead_time_days'
    ]

    X = df[features]

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.08,
        random_state=42
    )

    model.fit(X_sc)

    scores = model.decision_function(X_sc)

    metrics = {
        'contamination': 0.08,
        'n_estimators': 200,
        'features': features,
        'score_mean': round(float(scores.mean()), 4),
        'score_std': round(float(scores.std()), 4)
    }

    joblib.dump(model, os.path.join(MODEL_DIR, 'anomaly_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'anomaly_scaler.pkl'))
    joblib.dump(metrics, os.path.join(MODEL_DIR, 'anomaly_metrics.pkl'))

    print(f' Saved to {MODEL_DIR}')

    return metrics


if __name__ == '__main__':
    print('=' * 55)
    print(' American Computers Albania - ML Model Training')
    print('=' * 55)

    train_delay_model()
    train_forecast_model()
    train_anomaly_model()

    print('\nAll models trained and saved successfully.')
    print('=' * 55)