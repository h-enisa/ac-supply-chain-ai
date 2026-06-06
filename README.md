# AC Supply Chain AI
AI-powered supply chain management system for American Computers Albania — a real electronics retailer based in Tirana, Albania.

Advanced Software Engineering — Group Project

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

---

## Project Overview

AC Supply Chain AI is a full-stack web application that applies artificial intelligence and machine learning to the supply chain operations of American Computers Albania. The system provides:

- Demand forecasting using ARIMA models trained per product category
- Anomaly detection on order data using a hybrid rule-based pipeline
- Inventory management with real-time stock status tracking across 6 branches
- Supplier management with performance scoring and competitor price intelligence
- An AI Agent that generates prioritized reorder, reprice, and promote recommendations with step-by-step reasoning
- A public customer portal for checking product availability without login
- Secure authentication via JWT tokens with role-based access control

The system replaces manual spreadsheet-based tracking with an intelligent, data-driven dashboard accessible to supply chain managers.

---

## Team

| Name | Role | Branch |
|------|------|--------|
| Enisa Halilaj | Team Leader / Repo Master / API Endpoints / Tester | `enisa/api-endpoints` |
| Natalia Muca | Backend / Authentication | `natalia/backend-auth` |
| Sabina Merkaj | Database / Models | `sabina/database-models` |
| Alesia Palloshi | Frontend  | `alesia-palloshi/frontend` |
| Alesia Gjeta | ML / ETL / AI Agent | `alesia-gjeta/ml-models` |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.10) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| ML / Forecasting | scikit-learn, statsmodels (ARIMA) |
| Frontend | Plain HTML5 + Vanilla JavaScript |
| Charts | Chart.js |
| Authentication | JWT via python-jose, bcrypt |
| Email | Resend API |
| Version Control | Git / GitHub |

---

## System Architecture

```
+----------------------------------------------------------+
|                  Frontend (HTML/JS)                      |
|  Dashboard · Inventory · Orders · Suppliers · AI Agent   |
|  Demand Forecast · Anomaly Detection · Customer Portal   |
+-------------------------+--------------------------------+
                          |  HTTP / REST
+-------------------------v--------------------------------+
|                  FastAPI Backend                         |
|  Auth (JWT) · Products · Orders · Suppliers · ML Routes  |
|  Public Routes (no auth) · AI Agent Endpoints            |
+----------+-------------------------------+--------------+
           | SQLAlchemy ORM               | scikit-learn / statsmodels
+----------v-----------+     +-----------v--------------+
|    PostgreSQL DB      |     |     ML Model Layer       |
|  Branch / Supplier    |     |  ARIMA (per category)    |
|  Product / Inventory  |     |  Random Forest (delay)   |
|  Order / OrderItem    |     |  Anomaly Detection       |
|  DemandRecord / User  |     |  AI Agent / ETL          |
|  SearchLog            |     |  Priority Scoring        |
|  CompetitorPrice      |     |  Reasoning Engine        |
|  AgentRecommendation  |     +--------------------------+
+-----------------------+
```

---

## Features

### Authentication
- User registration and login via JWT
- Role-based access: admin, viewer
- Admin sees ETL Pipeline and User Management in sidebar
- All protected routes require a valid Bearer token
- Forgot password / reset password via Resend email API

### Inventory Management
- Full product catalogue with stock levels, prices, and categories
- Real-time status labels: In Stock, Low Stock, Out of Stock
- Per-branch stock breakdown across all 6 Albanian branches
- Linked to supplier records for traceability

### Demand Forecasting
- ARIMA models trained per product category (not a single generic model)
- Models saved to disk and loaded on demand — no re-training on every request
- Forecast output rendered as an interactive Chart.js line chart
- Year labels correctly reflect the 2025/2026 forecast horizon

### Anomaly Detection
- Hybrid approach: orders with ANOM-prefixed IDs are fetched and evaluated separately
- Rule-based thresholds applied to regular orders
- Each detected anomaly displayed with a score, type, and description

### Delay Prediction
- Random Forest classifier predicting shipment delay risk
- Inputs: distance, weather score, customs risk, supplier rating, lead time
- Returns risk class (LOW / MEDIUM / HIGH) with confidence and feature importance

### Route Optimizer
- Greedy heuristic for Albanian branch delivery network
- Optimizes by time, cost, or balanced objective
- Covers all 6 branch routes from Tirana and Durres

### Reorder Alerts
- Per-branch stock scanning — alerts when any branch falls below reorder point
- Critical vs warning urgency classification
- Suggested order quantity and days-until-stockout estimation

### AI Agent
- Priority scoring (0-100) combining stock ratio, days to stockout, demand, and price gap
- Step-by-step reasoning chain per recommendation (reorder, reprice, promote)
- Supplier comparison — ranks all suppliers for a category by combined performance score
- Agent memory — localStorage tracks approvals and dismissals
- Purchase Order PDF generation on reorder approval
- Agent chat with branch-specific queries, product lookup, and date-aware responses
- Proactive alerts badge showing current critical issue count

### Floating Chat Widget
- AC logo button fixed to bottom right
- Proactive alert summary on first open
- Voice input via Web Speech API (Chrome)
- Inline action buttons: View in AI Agent, View Price Intel

### Customer Portal
- Public page at /customer.html — no login required
- Search by name, SKU, or category
- Per-branch stock availability on each product card
- Silent search logging to database for demand gap analysis

### ETL Pipeline (admin only)
- Full data ingestion from PostgreSQL
- Cleaning, normalization, and feature engineering stages
- Train/test split export for ML models

---

## Project Structure

```
american_computers_backend/
├── main.py
├── requirements.txt
├── index.html                          [Alesia Palloshi]
├── login.html                          [Natali Muca]
├── reset-password.html                 [Natali Muca]
├── customer.html                       [Alesia Palloshi]
├── app/
│   ├── core/
│   │   ├── auth.py                     [Natali Muca]
│   │   └── config.py
│   ├── db/
│   │   └── session.py                  [Sabina Merkaj]
│   ├── models/
│   │   ├── models.py                   [Sabina Merkaj]
│   │   ├── user.py                     [Sabina Merkaj]
│   │   └── reset_token.py              [Sabina Merkaj]
│   ├── schemas/
│   │   ├── schemas.py
│   │   └── auth_schemas.py             [Natali Muca]
│   ├── api/
│   │   └── v1/
│   │       ├── router.py               [Enisa Halilaj / Natali Muca]
│   │       └── endpoints/
│   │           ├── auth.py             [Natali Muca]
│   │           ├── dashboard.py        [Enisa Halilaj]
│   │           ├── orders.py           [Enisa Halilaj]
│   │           ├── inventory.py        [Enisa Halilaj]
│   │           └── ml.py               [Alesia Gjeta]
│   ├── ml/
│   │   ├── train_models.py             [Alesia Gjeta]
│   │   ├── inference.py                [Alesia Gjeta]
│   │   └── trained_models/
│   └── services/
│       ├── etl_service.py              [Alesia Gjeta]
│       └── email_service.py            [Natali Muca]
└── scripts/
    └── seed_db.py                      [Sabina Merkaj]
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 16+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/h-enisa/ac-supply-chain-ai.git
cd ac-supply-chain-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the root folder:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/ac_logistics_db
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000
RESEND_API_KEY=your-resend-key
```

### 4. Seed the database (first time only)

```bash
python -m scripts.seed_db
```

### 5. Train the ML models (first time only)

```bash
python -m app.ml.train_models
```

### 6. Create new tables (if schema was updated)

```bash
python -c "from app.db.session import Base, engine; from app.models.models import *; Base.metadata.create_all(bind=engine)"
```

### 7. Start the backend

```bash
uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`

### 8. Start the frontend

Open a **second terminal** in the same project folder and run:

```bash
python -m http.server 3000
```

Then open your browser at: `http://localhost:3000/login.html`

---

## Pages

| Page | URL |
|------|-----|
| Login / Register | `http://localhost:3000/login.html` |
| Main Dashboard | `http://localhost:3000/index.html` |
| Customer Portal | `http://localhost:3000/customer.html` |
| API Docs | `http://localhost:8000/docs` |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login/form` | Login and receive JWT token |
| POST | `/auth/forgot-password` | Send password reset email |
| POST | `/auth/reset-password` | Reset password with token |
| GET | `/auth/users` | List all users (admin only) |
| PATCH | `/auth/users/{id}/deactivate` | Deactivate a user (admin only) |

### Public (no token required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/public/products` | Product availability for customer portal |
| POST | `/public/log-search` | Log customer search for demand analysis |

### Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory/` | List all inventory records |
| GET | `/products/` | List all products |
| GET | `/suppliers/` | List all suppliers |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | List all orders with status and delay risk |

### AI / ML
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ml/forecast` | ARIMA demand forecast for a category |
| POST | `/ml/delay/predict` | Random Forest delay prediction |
| GET | `/ml/anomalies` | Detect anomalies in recent orders |
| POST | `/ml/routes/optimize` | Optimize delivery routes |
| POST | `/ml/etl/run` | Trigger full ETL pipeline |
| GET | `/ml/reorder-alerts` | Per-branch reorder alerts with urgency |
| GET | `/ml/agent/recommendations` | AI agent recommendations with priority scores |
| GET | `/ml/agent/demand-gaps` | Customer demand gaps from search logs |
| GET | `/ml/agent/price-intelligence` | Competitor price comparison |
| GET | `/ml/agent/supplier-compare` | Supplier ranking for a category |
| GET | `/ml/agent/proactive-alerts` | Alert summary for floating chat badge |
| POST | `/ml/agent/chat` | Agent chat with intent routing |

All endpoints except `/auth/*` and `/public/*` require `Authorization: Bearer <token>`.

---

## Machine Learning Models

### Demand Forecasting (ARIMA)
- File: `app/ml/train_models.py`, `app/api/v1/endpoints/ml.py`
- Responsible: Alesia Gjeta
- Models are trained per product category using historical DemandRecord data
- Trained models are serialised to disk and loaded on subsequent requests
- Each forecast returns predicted quantities for the 2025/2026 horizon with confidence intervals

### Delay Prediction (Random Forest)
- File: `app/ml/inference.py`
- Responsible: Alesia Gjeta
- Classifies shipment delay risk as LOW, MEDIUM, or HIGH
- Inputs: distance, weather score, customs risk, supplier rating, lead time, route
- Returns probability, confidence, and top feature importances

### Anomaly Detection
- File: `app/ml/inference.py`
- Responsible: Alesia Gjeta
- Hybrid approach: ANOM-prefixed orders use dedicated rule-based evaluation
- Regular orders evaluated against stricter statistical thresholds
- Each anomaly has a score, type, severity, and description

### AI Agent Priority Scoring
- File: `app/api/v1/endpoints/ml.py`
- Responsible: Alesia Gjeta
- 0-100 score combining four signals:
  - Stock ratio vs reorder point: up to 40 points
  - Days until stockout: up to 15 points
  - Customer search demand: up to 25 points
  - Competitor price gap: up to 20 points

---

## Database Schema

Eight entities with the following key relationships:

```
SUPPLIER --(1:N)--> PRODUCT --(1:N)--> ORDER_ITEM
BRANCH   --(1:N)--> INVENTORY <--(1:1)-- PRODUCT
BRANCH   --(1:N)--> ORDER
ORDER    --(1:N)--> ORDER_ITEM
PRODUCT  --(1:N)--> COMPETITOR_PRICE
SEARCH_LOG          (standalone — customer intent tracking)
AGENT_RECOMMENDATION (standalone — persisted agent outputs)
DEMAND_RECORD       (standalone — aggregated by category for ARIMA)
USER                (standalone — managed by auth module)
```

Key design decisions:
- `order_ref` is a business key string enabling ANOM-prefix pattern matching
- `delay_risk` is a custom enum: `low | medium | high`
- `order_status` is a custom enum: `processing | in_transit | delivered | delayed | cancelled`
- `product.supplier_id` uses nullable FK preserving product records if a supplier is removed
- `SearchLog.searched_at` uses `server_default=func.now()` for reliable timestamping

---

## Database

- Name: `ac_logistics_db`
- Records: 507 orders · 103+ products · 6 branches · 10 EU suppliers
- To reseed from scratch:

```bash
psql -U postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python -m scripts.seed_db
python -m app.ml.train_models
```

---

AC Supply Chain AI — Advanced Software Engineering

American Computers Albania · Est. 2004 · Tirana, Albania
