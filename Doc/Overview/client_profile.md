# Client Profile — American Computers Albania

## Client Organisation

| Field | Details |
|-------|---------|
| **Organisation Name** | American Computers Albania |
| **Type** | Private Electronics Retailer |
| **Location** | Tirana, Albania |
| **Sector** | Consumer Electronics and IT Hardware |
| **Primary Contact** | Management / Operations Department |

---

## Organisation Overview

American Computers Albania is a Tirana-based electronics retailer specialising in consumer and business technology products. The company stocks and sells across six product categories — laptops, monitors, smartphones, peripherals, networking equipment, and accessories — and serves both individual customers and business clients throughout Albania.

The business operates from a central warehouse and retail operation in Tirana, managing supplier relationships, product procurement, and inventory distribution from a single location. As the Albanian consumer electronics market has grown, so has the complexity of managing stock levels, anticipating demand, and maintaining clean order records across a product catalogue of hundreds of SKUs.

### Product Portfolio

| Category | Description |
|----------|-------------|
| Laptops | Consumer and business laptops across multiple brands and price points |
| Monitors | Desktop displays, from budget to professional grade |
| Smartphones | Mobile devices, both retail and business procurement |
| Peripherals | Keyboards, mice, headsets, webcams, and accessories |
| Networking Equipment | Routers, switches, access points, and cabling |
| Accessories | Cables, cases, adapters, storage media, and consumables |

### Current Operations

**Strengths:**
- Established supplier network with consistent product availability
- Strong knowledge of the local Albanian market and customer base
- Central warehouse with existing inventory tracking processes
- Growing revenue and expanding product range year on year

**Challenges:**
- Inventory decisions made on experience and intuition rather than data
- No systematic forecasting — orders placed reactively when stock drops low
- Anomalous orders (duplicate entries, unusually large quantities, suspicious supplier activity) identified only after the fact, if at all
- No unified view of stock levels across all categories in real time
- Reporting done manually via spreadsheets, with significant lag time
- Supply chain visibility limited to whoever is physically in the warehouse

---

## Problem Statement

### The Current Situation

American Computers Albania manages its supply chain primarily through manual processes and spreadsheet-based tracking. As the product catalogue and order volume have grown, these processes have become increasingly error-prone and slow to respond to market changes.

#### Inventory Management

There is no real-time view of stock levels across all product categories in a single interface. Staff must check physical records or individual spreadsheets to understand what is in stock and what needs reordering. By the time a stockout is identified, the sales opportunity has often already been lost. Equally, overstocking in slow-moving categories ties up capital and warehouse space without return.

There is no automatic threshold alerting. A product can sit at critical stock levels for days before anyone notices and places a reorder.

#### Demand Forecasting

Purchasing decisions are based on historical experience rather than quantitative analysis. Seasonal patterns — for example, laptop demand rising before the academic year or networking equipment sales increasing in Q4 — are not formally modelled. This leads to both over-purchasing in categories that are softening and under-purchasing in categories where demand is building.

No tool currently exists to project demand per category over a one-to-three month horizon. The business cannot answer the question "how much stock should we hold in monitors next month" with any analytical confidence.

#### Anomaly Detection

Order irregularities — unusually high quantities, orders from atypical suppliers, duplicate order entries, or orders placed at unusual times — are not systematically flagged. These anomalies may indicate data entry errors, supplier issues, or procurement fraud. Currently they are identified only through manual review, which is infrequent and inconsistent.

There is no automatic mechanism to surface suspicious orders for manager review before they are processed.

---

## Requirements and Vision

### What American Computers Albania Needs

The client requires a unified, web-based platform that replaces manual spreadsheet management with a single intelligent system. The platform must address three core operational needs.

#### 1. Real-Time Inventory Visibility

A live dashboard that shows every product, its current stock quantity, and its status at a glance. Status should be derived automatically from thresholds (In Stock, Low Stock, Critical, Out of Stock) so a manager can scan the full catalogue in seconds rather than cross-referencing multiple spreadsheets.

#### 2. Data-Driven Demand Forecasting

A forecasting module that analyses historical order data per product category and generates a demand projection for the coming months. The forecast should be visual — a chart the manager can read without statistical training — and updated from live data. The goal is to give purchasing decisions a quantitative foundation rather than relying entirely on intuition.

#### 3. Automated Anomaly Detection

A detection layer that flags orders matching suspicious patterns before they are processed. The system must distinguish between orders that warrant high scrutiny (standard orders exceeding normal thresholds) and orders that are already pre-flagged as anomalous candidates (identified by a prefix in the order ID). Each flagged order must be presented with a type and a plain-language description so the manager understands what triggered the flag and can decide how to respond.

---

## Success Criteria

### Functional

- Inventory dashboard displays all products with live stock status and correct badge classification
- ARIMA forecasting generates per-category demand projections covering the 2025/2026 period
- Anomaly detection correctly flags irregular orders and presents each with a type and description
- Authentication system secures all data endpoints — no inventory or forecast data accessible without login
- System runs locally without dependency on external cloud services or APIs

### Operational

- A manager can assess the full inventory status of the warehouse in under 60 seconds using the dashboard
- Purchasing decisions for the next month can be informed by forecast data within 2 minutes of opening the system
- Anomalous orders are surfaced automatically — no manual review required to identify them
- System setup on a new machine takes under 10 minutes following the README

### Performance

- Inventory dashboard loads in under 2 seconds on a standard office machine
- Forecast endpoint responds within 3 seconds including model inference
- Anomaly detection processes the full order set in under 2 seconds

---

## Stakeholders

### Primary Users

**Warehouse and Operations Manager**
Needs the inventory dashboard as a daily operational tool. Must be able to identify stockouts and low-stock situations at a glance and act on them without navigating multiple systems. Does not have a technical background — the interface must communicate clearly without requiring knowledge of the underlying data model.

**Procurement Manager**
Uses the forecasting module to plan purchasing orders. Needs per-category projections they can use in supplier conversations and budgeting discussions. The value of the forecast is in its direction and trend, not its precision to the last unit.

**Finance and Compliance**
Has an interest in anomaly detection as a control mechanism. Flagged orders provide an audit trail that supports internal review processes and financial oversight. Needs to see anomaly type and description clearly enough to document a response.

### Secondary Stakeholders

**Suppliers**
Indirectly benefit from more accurate procurement. If American Computers Albania orders more consistently based on forecast data, supplier relationships become more predictable.

**IT Staff (if applicable)**
Responsible for setting up and maintaining the system. Must be able to install and run it from documentation alone without specialist knowledge of the codebase.

---

## Scope

### In Scope

- Secure login with JWT authentication
- Live inventory dashboard with status badges per product
- Per-category ARIMA demand forecasting with 2025/2026 projections
- Anomaly detection with ANOM-path and standard-path separation
- FastAPI backend serving all data endpoints
- PostgreSQL database with full supply chain schema (products, categories, suppliers, orders, order items, inventory records)
- Seed data representing American Computers Albania's real product categories
- HTML/JS frontend with Chart.js visualisations

### Out of Scope

- Multi-branch or multi-location inventory management (Phase 2)
- Supplier portal or external integrations
- Mobile application
- Email or push notification alerts for low stock
- Financial reporting and payment tracking
- Customer-facing interface

---

## Constraints

| Constraint | Detail |
|------------|--------|
| Deployment | Must run on standard hardware without cloud infrastructure — local deployment for Phase 1 |
| Data privacy | All product, order, and supplier data is internal — no customer personal data is stored in the system |
| Language | Interface in English for Phase 1; Albanian localisation deferred to Phase 2 |
| Dependencies | No external APIs required at runtime — all ML inference runs locally |
| Timeline | Phase 1 delivered within the academic project schedule |
| Team size | Five-person student team — scope must be achievable within available development hours |

---

## Key Decisions

### Technology Stack
FastAPI chosen for the backend due to natural integration with the Python ML ecosystem. PostgreSQL for the relational supply chain schema. statsmodels ARIMA for demand forecasting — interpretable and trainable on local hardware without GPU. Plain HTML/JS and Chart.js for the frontend to avoid build tooling overhead. JWT for authentication.

### Forecasting Approach
One ARIMA model trained per product category rather than a single pooled model. This isolates category-specific demand patterns — laptop seasonality should not influence the monitor forecast. Model evaluated on a held-out test period before being used for live projections.

### Anomaly Detection Design
Two detection paths: ANOM-prefixed orders are fetched separately and assessed with relaxed thresholds, since they are already candidate anomalies by design. Standard orders are assessed against stricter thresholds derived from the distribution of normal order quantities. This separation reduces false positives on regular order activity while maintaining sensitivity for known-suspect orders.

### Data Strategy
Seed data is generated programmatically to represent American Computers Albania's actual product categories and a realistic order history from 2023 to 2025. No real customer or transaction data is used in the system.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ARIMA produces poor forecasts for low-volume categories | Medium | Medium | Apply Holt-Winters or moving average as fallback for categories with sparse data; document per-category MAPE |
| Anomaly thresholds too aggressive — flags too many normal orders | Medium | Medium | Tune thresholds separately per detection path; validate against manually labelled test set before deployment |
| Inventory dashboard slow to load with large product catalogue | Low | Medium | Index FK columns in PostgreSQL; limit initial query to active products |
| Demo environment failure during live presentation | Low | High | Run demo on a local machine with app already running and seeded; prepare backup screenshots of each section |
| Seed data does not represent realistic seasonal patterns | Medium | Low | Generate order history with deliberate seasonal variation per category; review distribution before use |

---

*AC Supply Chain AI — Faculty of Information Technology*
*Client: American Computers Albania, Tirana*
