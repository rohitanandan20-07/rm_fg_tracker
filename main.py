# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.grn import router as grn_router
from api.issue import router as issue_router
from api.fg import router as fg_router
from api.dispatch import router as dispatch_router
from api.trace import router as trace_router
from api.blockchain_routes import router as blockchain_router
from api.materials import router as materials_router

from blockchain.audit_setup import ensure_blockchain_log_audit
from database.connection import engine

app = FastAPI(
    title="RM → FG Tracker API",
    description="Material tracking system with simulated blockchain",
    version="1.0.0"
)

# Streamlit (local + Render) → FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
        "https://rm-fg-tracker-dashboard.onrender.com",
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(grn_router)
app.include_router(issue_router)
app.include_router(fg_router)
app.include_router(dispatch_router)
app.include_router(trace_router)
app.include_router(blockchain_router)
app.include_router(materials_router)


@app.on_event("startup")
def _startup_init() -> None:
    # Ensure audit trail exists so Validate Chain can show diffs/history.
    # Never block API startup if DB role doesn't permit DDL in production.
    try:
        ensure_blockchain_log_audit(engine)
    except Exception as exc:
        print(f"[WARN] Audit setup skipped: {exc}")


@app.get("/")
def health_check():
    return {
        "status": "running",
        "system": "RM-FG Tracker",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/create-grn",
            "POST /api/issue-material",
            "POST /api/create-fg",
            "POST /api/dispatch",
            "GET  /api/trace/{material_id}",
            "GET  /api/validate-chain",
            "GET  /api/blockchain-log",
            "GET  /api/materials",
            "GET  /api/scan-events",
            "GET  /api/production-orders"
        ]
    }
