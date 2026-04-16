from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine
from app.models.models import Base
from app.ml.inference import ml_service


# ─── Startup / Shutdown ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: create DB tables and load ML models
    print("Starting American Computers Supply Chain API...")
    Base.metadata.create_all(bind=engine)
    print("Database tables ready.")
    ml_service.load_all()
    print("API ready.")
    yield
    # On shutdown (nothing to clean up for now)
    print("Shutting down.")


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## American Computers Albania — Supply Chain Analytics API

AI-powered backend for logistics optimization, demand forecasting,
delay prediction, and anomaly detection across all Albanian branches.

**Client:** American Computers Albania (american-pc.com)  
**Location:** Rruga Sulejman Delvina, Tirana, Albania  
**Branches:** Tirana · Shkodër · Elbasan · Vlorë · Berat · Pogradec

### Modules
- **Dashboard** — live KPIs and operational overview
- **Orders** — full order lifecycle management
- **Inventory** — stock levels across all branches
- **Suppliers** — EU supplier network and performance
- **AI / ML** — delay prediction, demand forecast, anomaly detection, route optimization
- **ETL** — data pipeline trigger and monitoring
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {
        "system":  "American Computers Albania — Supply Chain API",
        "version": settings.APP_VERSION,
        "status":  "online",
        "docs":    "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
