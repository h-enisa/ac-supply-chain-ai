# Research Plan — Technology Evaluation
**AC Supply Chain AI · American Computers Albania**
**Faculty of Information Technology**

---

## Overview

Before writing a single line of production code, each team member builds a small proof-of-concept (POC) for the technology they own. The purpose is straightforward: confirm that our chosen tools actually do what we need them to do, surface any surprises early, and give every member hands-on experience with their part of the stack before the full build begins.

Findings are logged in each member's personal wiki page. This research phase runs during **Week 1 and Week 2** and feeds directly into the architecture decisions recorded in the wiki.

---

## Why This Stack

**FastAPI (Python backend)**
We need a backend that integrates naturally with Python's data and ML ecosystem. FastAPI gives us async endpoints, automatic request validation via Pydantic, and auto-generated API docs — which matters when five people are working across frontend and backend at the same time and need a shared contract for what endpoints return.

**JWT Authentication**
The system has one class of user (retail staff) but every data endpoint must be protected. JWT is stateless, meaning no session table in the database, and the token carries enough information for the backend to identify the user without an extra DB lookup on every request. It is also the standard approach in FastAPI and well-documented.

**PostgreSQL + SQLAlchemy**
The supply chain domain is relational by nature. Products belong to categories, orders contain line items, inventory records link to products, suppliers appear on orders. PostgreSQL handles this well. SQLAlchemy lets us define the schema in Python, keeping the data model close to the application logic and out of separate migration files for Phase 1.

**statsmodels ARIMA + scikit-learn**
ARIMA is a proven method for monthly retail demand forecasting. It is interpretable — the professor can follow the methodology without a machine learning background — and it runs entirely on local hardware with no external API costs. scikit-learn handles the supporting work: preprocessing, anomaly scoring, and evaluation metrics. One model is trained per product category so that seasonal patterns in laptops do not contaminate the forecast for monitors.

**HTML + JavaScript + Chart.js**
The frontend does not need a framework. The interface is a single dashboard with three sections: inventory, forecasting, and anomaly detection. Vanilla JS handles the data fetching and DOM updates. Chart.js renders the ARIMA output as interactive charts. Keeping the frontend dependency-free means anyone on the team can read and modify it.

---

## Research Assignments

| Member | Technology | POC Goal | Pass Criteria |
|--------|------------|----------|---------------|
| Natali | FastAPI + JWT | Login endpoint returns signed JWT; protected route rejects bad tokens | POST /login returns token. GET /me returns 401 with no token. Password stored as bcrypt hash. |
| Sabina | PostgreSQL + SQLAlchemy | Define models, create tables, insert seed rows, run a FK join query | Tables created. Seed insert succeeds. Join query returns correct related objects. |
| Alesia Gjeta | statsmodels ARIMA | Fit model on 12 months of sample data, generate 3-month forecast, compute MAPE | Model fits without error. MAPE computed on held-out split. Forecast plotted and saved. |
| Alesia Palloshi | HTML + JavaScript + Chart.js | Dashboard page with Chart.js chart fed by a fetch() call; status badge function | Chart renders from fetched data. Badge returns correct colour for all 4 inventory states. |
| Enisa | FastAPI project structure + GitHub | Working project scaffold; all modules importable; README covers setup in under 5 steps | Clean clone runs with pip install + uvicorn. Branch workflow tested by all members. |

---

## What to Evaluate

**Setup time** — How long from zero to first working result? If setup takes more than a few hours, that is a signal worth noting.

**Error quality** — When something breaks, does the tool tell you what went wrong and where? Good error messages save hours during the main build.

**Integration** — Does this technology hand off cleanly to the next layer? A SQLAlchemy query result should feed naturally into a Pydantic schema. An ARIMA forecast array should be serialisable to JSON without conversion gymnastics.

**Stability** — Does the library have active maintenance? Are the docs current? Can you find answers to problems online without digging through outdated Stack Overflow threads?

**Cost** — Everything in this stack is open source and runs locally. Confirm there are no hidden rate limits, licence fees, or cloud dependencies that would surprise us during the demo.

---

## Detailed Research Tasks

### Backend and Authentication — Natali Muca

**Goal:** Confirm that FastAPI and JWT together can secure the full API surface of the system and that the authentication flow works correctly end to end.

**Tasks:**
- [x] Create FastAPI project with folder structure: `main.py`, `routers/auth.py`, `schemas/user.py`, `auth/jwt.py`
- [x] Implement POST `/auth/login` — validate username and password, return signed JWT
- [x] Hash passwords with `passlib[bcrypt]`; confirm no plaintext is ever written to the database
- [x] Sign tokens with `python-jose`; load secret key from `.env`
- [x] Create `get_current_user` dependency using `OAuth2PasswordBearer`
- [x] Apply the dependency to at least two protected routes
- [x] Confirm: request with no token returns 401
- [x] Confirm: request with expired or modified token returns 401
- [x] Set `ACCESS_TOKEN_EXPIRE_MINUTES` via environment variable
- [x] Document the full request lifecycle: login, token storage, protected request

**Questions to answer:**
- What is the minimum JWT payload needed — does `sub` alone suffice, or do we need role information in the token?
- How does token expiry interact with the frontend — does the client need to detect 401 and redirect, or can the backend handle it?
- Is there a meaningful security difference between storing the token in localStorage versus an httpOnly cookie for this use case?

**Done when:**
- POST `/login` responds in under 300ms locally
- 100% of invalid token test cases return 401
- No password or hash appears in any API response
- Another team member can protect a new route by adding one line

---

### Database and Data Models — Sabina Merkaj

**Goal:** Confirm that PostgreSQL and SQLAlchemy can represent the full supply chain schema and that seed data can be generated without constraint violations.

**Tasks:**
- [x] Connect to local PostgreSQL via SQLAlchemy engine with URL from `.env`
- [x] Define `Base` and the following models: `Category`, `Product`, `Supplier`, `Order`, `OrderItem`, `InventoryRecord`
- [x] Create all tables with `Base.metadata.create_all(engine)`
- [x] Write seed script: at least 6 categories, 30 products, 500 order records spanning 2023–2025
- [x] Seed ANOM-prefixed orders (`AC-2025-ANOM-001` etc.) for use in anomaly detection testing
- [x] Test FK constraint: insert a product with a non-existent `category_id` and confirm IntegrityError
- [x] Test join query: fetch all products in a category together with their current `InventoryRecord`
- [x] Implement inventory status derivation from quantity thresholds (In Stock / Low Stock / Critical / Out of Stock)
- [x] Verify session closes cleanly after each request — no open connections

**Questions to answer:**
- Should inventory status be a stored column updated by the API, or a computed property derived at query time from the quantity field?
- What quantity thresholds define each status level — and should these be configurable per category or global?
- How should `relationship()` and `back_populates` be structured between `Order` and `OrderItem` to avoid N+1 query problems?

**Done when:**
- All models create tables without error
- Seed script completes without constraint violations
- Join query returns correct related objects
- Status logic correctly classifies all four states

---

### Forecasting and Anomaly Detection — Alesia Gjeta

**Goal:** Confirm that ARIMA produces usable per-category forecasts from the seeded order data and that the hybrid anomaly detection logic correctly identifies flagged orders.

**Tasks:**
- [x] Extract monthly order totals per category from PostgreSQL using pandas
- [x] Build ETL pipeline: extract, aggregate by category and month, produce time-indexed DataFrame
- [x] Run Augmented Dickey-Fuller test on each category series; apply differencing where needed
- [x] Fit `ARIMA(p,d,q)` per category; evaluate `p` and `q` with ACF/PACF
- [x] Train on 2023–2024 data; test on first three months of 2025; compute MAPE and RMSE
- [x] Generate 12-month forecast (2025–2026) with 95% confidence intervals
- [x] Plot actuals vs forecast for each category; save as PNG
- [x] Implement anomaly detection in `inference.py`: define feature set (quantity, value, supplier, order timing)
- [x] Implement ANOM path: fetch orders with `AC-YYYY-ANOM-XXX` prefix separately, apply relaxed thresholds
- [x] Implement regular path: apply stricter thresholds (mean + 2 standard deviations) to standard orders
- [x] Label each flagged order with `anomaly_type` and `description`
- [x] Expose both forecast and anomaly results via FastAPI endpoints

**Questions to answer:**
- Does fitting one model per category outperform a single pooled model, and is the difference worth the added complexity?
- How should categories with sparse data (few non-zero months) be handled — fallback to Holt-Winters or simple moving average?
- Why does the ANOM detection path use relaxed thresholds rather than stricter ones — what does that design decision prevent?

**Done when:**
- ARIMA fits on all six product categories without convergence warnings
- MAPE below 20% on the test split for at least four of six categories
- Anomaly detection flags all manually injected ANOM orders in the test set
- `inference.py` imports cleanly from the FastAPI router with no circular dependency

---

### Frontend and User Interface — Alesia Palloshi

**Goal:** Confirm that plain HTML/JS and Chart.js can deliver a functional, responsive inventory dashboard without a frontend framework.

**Tasks:**
- [x] Create `index.html` with navigation between Inventory, Forecast, and Anomaly sections
- [x] Store JWT from login response; attach as `Authorization: Bearer` header on all subsequent fetch calls
- [x] Build inventory table: renders rows dynamically from the `/inventory` API response
- [x] Implement `renderBadge(quantity)`: returns colour-coded HTML element for each of the four status states
- [x] Integrate Chart.js: render per-category ARIMA forecast as a line chart from `/forecast` response
- [x] Build anomaly panel: fetch from `/anomalies`, display `anomaly_type` and `description` per flagged order
- [x] Confirm Chart.js data can be updated via `chart.data.datasets[0].data` and `chart.update()` without recreating the canvas
- [x] Test responsive layout from 360px to 1440px
- [x] Test 401 handling: expired token redirects to login rather than showing a blank screen
- [x] QA full user flow: login, inventory, forecast, anomaly — no broken state between sections

**Questions to answer:**
- Can the Chart.js instance be updated in place, or does the canvas need to be destroyed and recreated on each data change?
- What colour values for the four badge states pass WCAG AA contrast requirements?
- How should the UI behave if the forecast endpoint is slow (ARIMA can take one to two seconds) — loading state, or just wait?

**Done when:**
- Full login-to-dashboard flow completes without a page reload
- Status badges are correct for all four states across all inventory rows
- Forecast chart renders with correct 2025/2026 labels
- Anomaly panel shows type and description for each flagged order
- Layout holds at 360px, 768px, and 1280px

---

### Architecture and Project Scaffold — Enisa Halilaj

**Goal:** Define the folder structure and GitHub workflow that the whole team operates within, and confirm the project can be set up from a clean clone in under five minutes.

**Tasks:**
- [x] Define project folders: `backend/`, `frontend/`, `ml/`, `docs/`
- [x] Scaffold `backend/`: `main.py`, `database.py`, `routers/`, `models/`, `schemas/`, `auth/`
- [x] Configure `.env` for `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`; add `.env.example`; add `.env` to `.gitignore`
- [x] Write `requirements.txt` with pinned versions for all dependencies
- [x] Write `README.md`: project description, installation, how to run, folder structure
- [x] Create GitHub repo, set branch protection on `main`, define naming convention
- [x] Document PR workflow: branch, commit, push, PR, review, merge
- [x] Verify: `pip install -r requirements.txt` followed by `uvicorn main:app` is the full setup
- [x] Confirm `ml/inference.py` can be imported from `routers/` without circular imports
- [x] Produce all required diagrams: Use Case, Activity, State, ERD, DFD Level 0 and Level 1, BPMN

**Questions to answer:**
- How should the `ml/` folder be structured so that inference and training steps are clearly separated?
- Does `database.py` own the session factory, or should each router manage its own session lifecycle?
- Which diagrams require draw.io and which can be produced in Mermaid — and does the grading rubric specify?

**Done when:**
- Project runs from a clean clone following the README alone
- All five members have pushed to a feature branch and opened a PR
- No credentials appear anywhere in git history
- Circular import between `ml/` and `routers/` confirmed absent

---

## Research Log Template

Each member logs findings in their personal wiki page under a `## Research Log` section. Use this format for each entry.

```markdown
### [Date] — [Technology] — [What was tested]

**What was built:**
Short description of the POC or test.

**What worked:**
Specific positive findings.

**What did not work:**
Blockers, confusing behaviour, documentation gaps.

**Key finding:**
One or two sentences — the main takeaway.

**Metrics:**
Response time: ms / Model MAPE: % / Rows processed: N

**Recommendation:**
Proceed as planned, adjust approach, or flag for team discussion.

**Links:**
GitHub branch or file, documentation page consulted.
```

---

## Milestones

| Milestone | Target | Owner | Output |
|-----------|--------|-------|--------|
| Kickoff and assignments | Week 1, Day 1 | Enisa | Repo created, branches set up, assignments confirmed |
| POCs working | Week 1, Day 5 | All | Each POC runs without error on local machine |
| First log entries | Week 2, Day 2 | All | Wiki pages updated with initial findings |
| Team review | Week 2, Day 3 | Enisa | Meeting to surface blockers and confirm architecture |
| Architecture locked | Week 2, Day 5 | Enisa | Module boundaries agreed, interface contracts documented |
| Development begins | Week 3 | All | Feature branches created, implementation starts |

---

## If Something Does Not Work

Not every technology choice will be validated without issues. If a blocker comes up:

1. Log it in your wiki page the same day it is found.
2. Raise it in the team chat — do not wait for the weekly meeting if it is blocking progress.
3. At the team review, decide: is this fixable within the current technology, or do we pivot?
4. Document whatever is decided, including the reasoning.

**Fallback options:**
- ARIMA does not converge for a category: apply Holt-Winters or a simple moving average for that category only
- SQLAlchemy session management causes connection pool issues: switch to explicit `with Session(engine) as session:` context managers throughout
- Chart.js in-place update does not work as expected: call `chart.destroy()` before reinitialising with new data
- JWT implementation blocks frontend progress: use a hardcoded dev token to unblock the UI while auth is finalised, and remove it before the merge

---

## Handoff

When the research phase is complete, each POC becomes the starting point for the real module — no throwaway code. Enisa collects the findings from all wiki pages, documents the final architecture decisions with their rationale, and locks the module boundary contracts (what each endpoint returns, what each layer expects as input) before Week 3 begins.

---

*Repository: github.com/h-enisa/ac-supply-chain-ai*
*AC Supply Chain AI — Faculty of Information Technology*
