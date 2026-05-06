#  AC Supply Chain AI

> AI-powered supply chain management system for **American Computers Albania** — a real electronics retailer based in Tirana, Albania.
>
> *Advanced Software Engineering — Group Project*

---

## Table of Contents

- [Project Overview](#project-overview)
- [Team](#team)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Machine Learning Models](#machine-learning-models)
- [Database Schema](#database-schema)
- [Diagrams](#diagrams)
- [Testing](#testing)

---

## Project Overview

AC Supply Chain AI is a full-stack web application that applies artificial intelligence and machine learning to the supply chain operations of American Computers Albania. The system provides:

- **Demand forecasting** using ARIMA models trained per product category
- **Anomaly detection** on order data using a hybrid rule-based + ML pipeline
- **Inventory management** with real-time stock status tracking
- **Supplier management** with linked product inventories
- **Secure authentication** via JWT tokens

The system replaces manual spreadsheet-based tracking with an intelligent, data-driven dashboard accessible to supply chain managers.

---

## Team

| Name | Role | Responsibilities |
|---|---|---|
| **Enisa Halilaj** | Team Leader / Repo Master | Project coordination, GitHub management, CI, documentation |
| **Natali Muca** | Backend / Authentication | FastAPI routes, JWT auth middleware, API endpoints, `auth.py`, `main.py`, `schemas.py` |
| **Sabina Merkaj** | Database / Models | PostgreSQL schema, SQLAlchemy models, migrations, `models.py`, `database.py`, `seed_db.py` |
| **Alesia Palloshi** | Frontend / Tester | HTML/JS pages, Chart.js integration, manual QA, all files under `frontend/` |
| **Alesia Gjeta** | ML / ETL | ARIMA demand forecasting, anomaly detection, `forecasting.py`, `inference.py`, `etl.py` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) |
| **ORM** | [SQLAlchemy](https://www.sqlalchemy.org/) |
| **ML / Forecasting** | [scikit-learn](https://scikit-learn.org/), [statsmodels](https://www.statsmodels.org/) (ARIMA) |
| **Frontend** | Plain HTML5 + Vanilla JavaScript |
| **Charts** | [Chart.js](https://www.chartjs.org/) |
| **Authentication** | JWT (JSON Web Tokens) via [python-jose](https://github.com/mpdavis/python-jose) |
| **Version Control** | Git / GitHub |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                  │
│   Dashboard · Inventory · Forecast · Anomalies · Suppliers│
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP / REST
┌──────────────────────▼──────────────────────────────────┐
│                 FastAPI Backend                          │
│   Auth (JWT) · Products · Orders · Suppliers · ML Routes │
└────────┬─────────────────────────────────┬──────────────┘
         │ SQLAlchemy ORM                  │ scikit-learn / statsmodels
┌────────▼──────────┐          ┌───────────▼──────────────┐
│   PostgreSQL DB   │          │     ML Model Layer       │
│  Supplier/Product │          │  ARIMA (per category)    │
│  Order/AnomalyLog │          │  Anomaly Detection       │
│  DemandRecord/User│          │  ETL Pipeline            │
└───────────────────┘          └──────────────────────────┘
```

---

## Features

###  Authentication
- User registration and login via JWT
- Role-based access: `admin`, `manager`, `viewer`
- All protected routes require a valid Bearer token

###  Inventory Management
- Full product catalogue with stock levels, prices, and categories
- Real-time status labels: **In Stock**, **Low Stock**, **Out of Stock**
- Linked to supplier records for traceability

###  Demand Forecasting
- ARIMA models trained **per product category** (not a single generic model)
- Models saved to disk and loaded on demand — no re-training on every request
- Forecast output rendered as an interactive Chart.js line chart
- Year labels correctly reflect the 2025/2026 forecast horizon

###  Anomaly Detection
- **Hybrid approach**: orders with `ANOM`-prefixed IDs are fetched and evaluated separately
- Rule-based thresholds applied to regular orders (stricter) vs. known anomalous orders
- Each detected anomaly stored in `anomaly_log` with a score, reason, and timestamp

###  Supplier Management
- Full CRUD for suppliers (name, contact email, country)
- Products linked to suppliers via foreign key with `ON DELETE SET NULL`

---

## Project Structure

```
ac-supply-chain-ai/
│
├── backend/
│   ├── main.py            # FastAPI app entrypoint, route registration     [Natali]
│   ├── auth.py            # JWT token creation, hashing, middleware        [Natali]
│   ├── schemas.py         # Pydantic request/response schemas              [Natali]
│   ├── models.py          # SQLAlchemy ORM models                          [Sabina]
│   ├── database.py        # DB engine, session factory                     [Sabina]
│   ├── seed_db.py         # Database seeding with realistic test data      [Sabina]
│   ├── forecasting.py     # ARIMA per-category training and prediction     [Alesia G.]
│   ├── inference.py       # Hybrid anomaly detection pipeline              [Alesia G.]
│   └── etl.py             # ETL pipeline for demand records                [Alesia G.]
│
├── frontend/
│   ├── index.html         # Dashboard (KPIs + Chart.js forecast)           [Alesia P.]
│   ├── inventory.html     # Inventory table with status badges             [Alesia P.]
│   ├── forecast.html      # Demand forecast chart page                     [Alesia P.]
│   ├── anomalies.html     # Anomaly detection results page                 [Alesia P.]
│   ├── suppliers.html     # Supplier management page                       [Alesia P.]
│   └── js/
│       └── api.js         # Shared API call helpers + auth token handling  [Alesia P.]
│
├── docs/
│   ├── diagrams/          # UML (Use Case, Activity, State), ERD, DFD     [Enisa]
│   └── meeting_reports/   # Weekly meeting reports (Weeks 1–4)
│
├── requirements.txt       # Python dependencies                            [Enisa]
├── .gitignore                                                              [Enisa]
└── README.md                                                               [Enisa]
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/h-enisa/ac-supply-chain-ai.git
cd ac-supply-chain-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Create a PostgreSQL database and set the connection string:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/ac_supply_chain"
export SECRET_KEY="your-secret-key-here"
```

### 5. Run migrations and seed data

```bash
cd backend
python seed_db.py
```

This creates all tables and inserts realistic test data including 7 anomalous orders with `ANOM`-prefixed IDs.

### 6. Start the server

```bash
uvicorn backend.main:app --reload --port 8000
```

### 7. Open the frontend

Open `frontend/index.html` in your browser, or serve it with:

```bash
python -m http.server 5500 --directory frontend
```

Then navigate to `http://localhost:5500`.

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT token |

### Products
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products/` | List all products with inventory status |
| `GET` | `/products/{id}` | Get single product detail |
| `POST` | `/products/` | Create new product *(admin only)* |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/orders/` | List all orders |
| `GET` | `/orders/anomalies` | List orders flagged as anomalous |

### Forecasting
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/forecast/{category}` | Get ARIMA demand forecast for a category |

### Anomalies
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/anomalies/` | List all detected anomalies with scores and reasons |

### Suppliers
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/suppliers/` | List all suppliers |
| `POST` | `/suppliers/` | Create supplier *(admin only)* |
| `PUT` | `/suppliers/{id}` | Update supplier |
| `DELETE` | `/suppliers/{id}` | Delete supplier |

> All endpoints except `/auth/*` require a valid `Authorization: Bearer <token>` header.

---

## Machine Learning Models

### Demand Forecasting (ARIMA)

- **File**: `backend/forecasting.py`
- **Responsible**: Alesia Gjeta
- Models are trained **per product category** using historical `DemandRecord` data
- Trained models are serialised to disk (pickle) and loaded on subsequent requests — avoiding redundant re-training
- Each forecast returns predicted quantities for the 2025/2026 horizon

### Anomaly Detection

- **File**: `backend/inference.py`
- **Responsible**: Alesia Gjeta
- **Hybrid approach**:
  1. Orders with `ANOM`-prefixed IDs (e.g., `AC-2025-ANOM-001`) are identified and processed through a dedicated rule-based evaluation path
  2. All other orders are evaluated against stricter statistical thresholds
- Detected anomalies are written to the `anomaly_log` table with a score, reason, and detection timestamp

---

## Database Schema

Six entities with the following key relationships:

```
SUPPLIER ──(1:N)──► PRODUCT ──(1:N)──► ORDER ──(1:1)──► ANOMALY_LOG

DEMAND_RECORD   (standalone — aggregated by category, used by ARIMA)
USER            (standalone — managed by auth module)
```

Key design decisions:
- `order_id` is a business key string (`VARCHAR(30)`) not an auto-increment, enabling ANOM-prefix pattern matching
- `delay_risk` is a custom PostgreSQL ENUM: `low | medium | high`
- `anomaly_log.order_id` has a `UNIQUE` constraint enforcing the 0..1 relationship shown in the ERD
- `product.supplier_id` uses `ON DELETE SET NULL` to preserve product records if a supplier is removed

---

## Diagrams

All diagrams are in `docs/diagrams/`:

| Diagram | Notation | Description |
|---|---|---|
| Use Case | UML | Manager, ML System (timer), Supplier actors; 6 use cases |
| Activity | UML | Demand forecasting workflow with model-cache decision branch |
| State | UML | Inventory item lifecycle (In Stock → Low Stock → Out of Stock → On Order) |
| ERD | Crow's Foot / ERDPlus | 6 entities, PK/FK badges, cardinality notation |
| DFD | Level 0 (Context) | External entities, central process, 3 data stores |

---

## Testing

Manual test cases were executed by **Alesia Palloshi** across all major user flows:

- Authentication (register, login, invalid credentials, token expiry)
- Inventory listing and status display
- Demand forecast chart rendering with real API data
- Anomaly detection results page
- Supplier CRUD operations
- Chart.js tooltip and label accuracy (including 2025/2026 year labels)

> Automated tests are planned for a future iteration.

---

*AC Supply Chain AI — Advanced Software Engineering*