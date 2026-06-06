# Project Description — AC Supply Chain AI

## Project Overview

| Field | Details |
|-------|---------|
| **Project Name** | AC Supply Chain AI |
| **Client** | American Computers Albania |
| **Client Type** | Electronics Retailer |
| **Client Location** | Tirana, Albania |
| **Project Type** | AI-Powered Supply Chain Management System |
| **Phase** | Phase 1 — Core System |
| **Repository** | github.com/h-enisa/ac-supply-chain-ai |
| **Institution** | Faculty of Information Technology |

---

## What Was Built

AC Supply Chain AI is a web-based platform that gives American Computers Albania's retail managers a unified, data-driven view of their supply chain. The system replaces manual spreadsheet-based inventory tracking and intuition-led purchasing decisions with three integrated capabilities: a live inventory dashboard, a per-category demand forecasting module powered by ARIMA, and an automated anomaly detection layer that flags irregular orders before they are processed.

The system is built on a FastAPI backend, a PostgreSQL database, and a plain HTML/JavaScript frontend with Chart.js visualisations. All machine learning inference runs locally — no external APIs or cloud services are required at runtime.

---

## The Problem

American Computers Albania manages a product catalogue spanning six categories — laptops, monitors, smartphones, peripherals, networking equipment, and accessories — across a central warehouse in Tirana. As the business has grown, three operational problems have become increasingly costly.

**Reactive inventory management.** There is no real-time view of stock levels across all categories in a single place. Stockouts and overstock situations are identified after the fact, resulting in lost sales or unnecessary capital tied up in slow-moving products.

**No quantitative basis for purchasing.** Procurement decisions are made on experience and intuition rather than data. Seasonal demand patterns — laptop sales rising before the academic year, networking equipment peaking in Q4 — are not formally modelled, leading to both under- and over-purchasing across different categories.

**Undetected order anomalies.** Irregular orders — unusually high quantities, atypical supplier combinations, duplicate entries — are not systematically identified. The current process relies on infrequent manual review, which means anomalies can move through the procurement pipeline undetected.

---

## The Solution

### Inventory Dashboard

A live dashboard displays every product in the catalogue with its current stock quantity and an automatically derived status badge. Status is calculated from configurable thresholds: In Stock, Low Stock, Critical, and Out of Stock. A manager can assess the full warehouse at a glance without opening a spreadsheet or coordinating with warehouse staff.

### Demand Forecasting

The forecasting module fits a separate ARIMA model for each product category using historical order data from 2023 to 2025. Each model generates a demand projection through 2026, presented as an interactive Chart.js line chart. The per-category approach ensures that seasonal patterns in one product type do not distort the forecast for another. Model accuracy is evaluated on a held-out test period using MAPE and RMSE before forecasts are served to the frontend.

### Anomaly Detection

The anomaly detection layer implements two parallel detection paths. Orders carrying an ANOM prefix in their identifier (for example, AC-2025-ANOM-001) are pre-flagged as candidate anomalies and assessed against relaxed thresholds. Standard orders are assessed against stricter thresholds derived from the statistical distribution of normal order quantities. Every flagged order is presented in the UI with an anomaly type and a plain-language description, giving the manager enough context to decide how to respond without needing to inspect the raw data.

### Authentication

All data endpoints are protected by JWT authentication. Users log in with a username and password, receive a signed token, and every subsequent request carries that token as a bearer credential. Passwords are stored as bcrypt hashes. No session state is held server-side.

---

## Architecture

```
Frontend (HTML / JavaScript / Chart.js)
         |
         | fetch() with Authorization: Bearer
         |
Backend (Python / FastAPI)
    |              |               |
routers/       routers/        routers/
inventory      forecast        anomalies
    |              |               |
models/        ml/             ml/
SQLAlchemy     inference.py    inference.py
    |
database.py
    |
PostgreSQL
```

The frontend communicates with the backend exclusively through JSON API endpoints. The ML layer (inference.py) is imported by the forecasting and anomaly routers and runs in-process — no separate model server. The database layer uses SQLAlchemy ORM throughout; no raw SQL is used in the application code.

---

## Technical Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend framework | FastAPI (Python) | API routing, request validation, dependency injection |
| Authentication | JWT via python-jose + passlib/bcrypt | Stateless token-based auth |
| Database | PostgreSQL | Relational storage for all supply chain data |
| ORM | SQLAlchemy | Model definition, query building, session management |
| Forecasting | statsmodels ARIMA | Per-category demand time series modelling |
| ML utilities | scikit-learn | Preprocessing, evaluation metrics, anomaly scoring |
| ETL | pandas | Data extraction, aggregation, time-series indexing |
| Frontend | HTML + JavaScript | Dashboard layout, data fetching, DOM rendering |
| Charts | Chart.js | Forecast visualisation, interactive line and bar charts |
| Version control | GitHub | Source control, branch management, collaboration |

---

## Data Model

The PostgreSQL schema covers the core entities of the supply chain domain.

| Model | Description |
|-------|-------------|
| Category | Product categories (Laptops, Monitors, Smartphones, Peripherals, Networking, Accessories) |
| Product | Individual SKUs with name, category FK, and base price |
| Supplier | Supplier records linked to orders |
| Order | Purchase orders with date, supplier, and status |
| OrderItem | Line items within each order — product, quantity, unit price |
| InventoryRecord | Current stock quantity per product, from which status is derived |

Seed data covers 6 categories, 30+ products, and approximately 500 order records spanning 2023 to 2025, including a set of ANOM-prefixed orders used to validate anomaly detection.

---

## Team

| Member | Role | Owned Files |
|--------|------|-------------|
| Enisa Halilaj | Team Leader, Repo Master, Documentation | `main.py`, `requirements.txt`, `README.md`, `docs/`, architecture diagrams |
| Natali Muca | Backend, JWT Authentication | `backend/routers/`, `backend/auth/`, `backend/schemas/` |
| Sabina Merkaj | Database, SQLAlchemy Models, Seed Data | `backend/models/`, `backend/database.py`, `backend/seed.py` |
| Alesia Palloshi | Frontend, QA Testing | `frontend/` |
| Alesia Gjeta | ML Models, ARIMA Forecasting, Anomaly Detection, ETL | `ml/` |

### Contribution Summary

**Enisa Halilaj** defined the project architecture, produced all UML diagrams (Use Case, Activity, State Machine), ERD, DFD (Level 0 and Level 1), and BPMN swimlane diagrams. Managed the GitHub repository, reviewed and merged all pull requests, wrote the README, and produced the full wiki including weekly meeting reports and per-member wiki pages.

**Natali Muca** implemented the FastAPI authentication layer end to end: user login endpoint, bcrypt password hashing, JWT signing with python-jose, the `get_current_user` dependency, and protection of all data routes. Responsible for the backend's security surface.

**Sabina Merkaj** designed and implemented all six SQLAlchemy models, the database connection setup, and the seed script that populates the system with realistic electronics product and order data. Defined inventory status derivation logic and threshold values.

**Alesia Palloshi** built the complete HTML/JavaScript frontend: the inventory table with status badges, Chart.js forecast charts, anomaly detection panel, login flow with JWT storage and bearer header attachment, and responsive layout. Conducted QA testing across all features before each PR was merged.

**Alesia Gjeta** built the full ML pipeline: ETL extraction from PostgreSQL via pandas, ADF stationarity testing, per-category ARIMA fitting and evaluation, 2025/2026 forecast generation, and the hybrid anomaly detection logic in inference.py including the ANOM-prefix path and the standard rule-based path. Connected the ML output to FastAPI endpoints.

---

## Key Design Decisions

**One ARIMA model per category, not a pooled model.**
A single model trained across all categories would average out category-specific seasonal signals. Laptops and networking equipment have different demand curves. Fitting independently per category keeps those signals intact, at the cost of needing more training runs. For six categories this is computationally trivial.

**Two-path anomaly detection.**
Flagging every order above a single threshold would generate too many false positives on high-volume categories. The ANOM prefix path handles orders already identified as suspicious candidates and applies relaxed scoring — they are evaluated, not assumed guilty. Standard orders are held to a stricter statistical threshold. This design reduces noise in the manager's anomaly view.

**Plain HTML/JS frontend over a framework.**
The frontend is a single dashboard, not a multi-page application with complex state. Adding React or Vue would introduce a build pipeline, a dependency tree, and a learning curve with no functional benefit at this scope. Vanilla JS keeps the frontend readable by every team member.

**SQLAlchemy ORM throughout, no raw SQL.**
Keeping all database interaction in the ORM layer means schema changes propagate through the model definitions rather than requiring SQL updates scattered across multiple files. It also makes the data model self-documenting.

---

## Deliverables

### System

- Functional web application with login, inventory dashboard, forecasting charts, and anomaly detection panel
- FastAPI backend with authenticated endpoints for inventory, forecast, and anomaly data
- PostgreSQL database with full supply chain schema and realistic seed data
- ARIMA models fitted and evaluated per product category
- Hybrid anomaly detection covering both ANOM-prefixed and standard orders

### Documentation

- README with installation and setup instructions
- GitHub wiki with architecture overview, per-member contribution pages, and weekly meeting reports (Weeks 1 through 5)
- Use Case, Activity, and State Machine UML diagrams
- Entity-Relationship Diagram (Chen notation and crow's foot)
- Data Flow Diagrams, Level 0 and Level 1
- BPMN swimlane process diagram
- System design wireframes (12 pages, hand-drawn style)
- Presentation slide deck (12 slides) with speaker script

---

## Outcomes

The Phase 1 system delivers against all three core requirements defined in the client brief.

A warehouse manager can open the inventory dashboard and immediately see which products are In Stock, Low Stock, Critical, or Out of Stock — for the full catalogue — without accessing a spreadsheet or speaking to warehouse staff.

A procurement manager can open the forecasting module and view per-category demand projections through 2026, providing a quantitative basis for purchasing decisions that did not exist before.

An operations manager reviewing orders can see all anomalous orders surfaced automatically, each with a type and a plain-language description, with no manual review required.

---

## Phase 2 Opportunities

| Feature | Description |
|---------|-------------|
| Multi-branch inventory | Extend the data model to support multiple locations; aggregate and per-branch views |
| Automated reorder alerts | Trigger email or in-app notifications when a product reaches Critical status |
| Supplier portal | External interface for suppliers to view purchase orders and confirm shipments |
| Financial reporting | Procurement cost tracking, budget vs actual, category-level spend analysis |
| Mobile interface | Responsive mobile view or dedicated app for warehouse floor use |
| Enhanced ML | Category-level anomaly detection; SARIMA for stronger seasonal modelling |

---

*AC Supply Chain AI — Faculty of Information Technology*
*Client: American Computers Albania, Tirana*
