# American Computers Albania - Supply Chain AI System
AI-powered supply chain management system built for American Computers Albania.
## Tech Stack
- Backend: FastAPI + PostgreSQL + SQLAlchemy
- ML Models: Random Forest, ARIMA, Isolation Forest
- Frontend: HTML/CSS/JavaScript + Chart.js
- Auth: JWT + bcrypt
## Team
- Enisa (Leader) - API Endpoints
- Natalia - Backend and Authentication
- Sabina - Database and Models
- Alesia Palloshi - Frontend
- Alesia Gjeta - Machine Learning
## Setup
1. pip install -r requirements.txt
2. Copy .env.example to .env and fill in values
3. Create database ac_logistics_db in pgAdmin
4. py -3.10 -m scripts.seed_db
5. py -3.10 -m app.ml.train_models
6. uvicorn main:app --reload
7. py -3.10 -m http.server 3000
8. Open http://localhost:3000/login.html