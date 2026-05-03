"""
backend/app.py

FastAPI application entry-point for the Multi-Modal Stroke Risk Detection system.

Registers:
    POST /analyze-face    → routes/face.py
    POST /analyze-speech  → routes/speech.py
    POST /predict         → routes/fusion.py
    GET  /docs            → Swagger UI (auto-generated)
    GET  /health          → Health check
    GET  /                → Serves frontend/index.html

Startup:
    On first launch, both AI models are pre-loaded into memory so that
    the first API call does not incur a cold-start delay.
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Route imports ─────────────────────────────────────────────────────────────
from backend.routes.face   import router as face_router
from backend.routes.speech import router as speech_router
from backend.routes.fusion import router as fusion_router
from backend.routes.chatbot import router as chatbot_router
from backend.routes.reports import router as reports_router
from backend.routes.auth import router as auth_router

# ── Model pre-loaders ─────────────────────────────────────────────────────────
from backend.models.face_model.face_model     import load_model as load_face_model
from backend.models.speech_model.speech_model import load_model as load_speech_model

# ── Logging configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent          # d:/sem project/
FRONTEND_DIR = BASE_DIR / "frontend"

# ═══════════════════════════════════════════════════════════════════════════════
#  APPLICATION FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Multi-Modal AI Framework for Early Stroke Risk Detection",
    description=(
        "Detects stroke risk by analyzing **facial asymmetry** (CNN + geometric "
        "landmark analysis) and **speech abnormalities** (MFCC + LSTM emotion "
        "detection). Uses a weighted fusion model: "
        "`final_score = 0.6 × face_score + 0.4 × speech_score`."
    ),
    version="1.0.0",
    contact={
        "name": "Stroke Detection Team",
        "email": "team@strokedetect.ai",
    },
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow all origins in development; tighten for production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API routers ──────────────────────────────────────────────────────
app.include_router(face_router,   tags=["Face Analysis"])
app.include_router(speech_router, tags=["Speech Analysis"])
app.include_router(fusion_router, tags=["Multi-Modal Fusion"])
app.include_router(chatbot_router, tags=["Chatbot"])
app.include_router(reports_router, tags=["Clinical Reports & Integration"])
app.include_router(auth_router, tags=["Authentication"])

# ── Static files (frontend) ───────────────────────────────────────────────────
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    logger.info("Serving frontend from %s", FRONTEND_DIR)


# ═══════════════════════════════════════════════════════════════════════════════
#  STARTUP / SHUTDOWN EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Pre-load AI models on startup to avoid cold-start latency on first request."""
    logger.info("=== Stroke Detection Server Starting ===")
    from backend.utils.db import connect_to_mongo
    await connect_to_mongo()
    
    try:
        load_face_model()
        logger.info("✓ Face model loaded.")
    except Exception as exc:
        logger.warning("Face model pre-load failed (will retry on first request): %s", exc)

    try:
        load_speech_model()
        logger.info("✓ Speech model loaded.")
    except Exception as exc:
        logger.warning("Speech model pre-load failed (will retry on first request): %s", exc)

    logger.info("=== Server ready. Visit http://localhost:8000 ===")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== Stroke Detection Server Shutting Down ===")
    from backend.utils.db import close_mongo_connection
    await close_mongo_connection()


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["Utility"], summary="Health check")
async def health_check():
    """Returns server status and model availability."""
    from backend.models.face_model.face_model     import _face_model
    from backend.models.speech_model.speech_model import _speech_model

    return JSONResponse({
        "status":         "healthy",
        "face_model":     "loaded" if _face_model is not None else "not loaded",
        "speech_model":   "loaded" if _speech_model is not None else "not loaded",
        "version":        "1.0.0",
        "endpoints": {
            "analyze_face":   "POST /analyze-face",
            "analyze_speech": "POST /analyze-speech",
            "predict":        "POST /predict",
            "docs":           "GET  /docs",
        },
    })


@app.get("/research-metrics", tags=["Utility"], summary="Get research-grade validation metrics")
async def get_metrics():
    """Returns academic validation metrics (Accuracy, Datasets, AUC-ROC)."""
    from backend.utils.validator import get_research_metrics
    return JSONResponse(get_research_metrics())


@app.get("/history", tags=["Utility"], summary="Get patient analysis history")
async def get_history_route():
    """Returns the last 10 analysis results for trend tracking."""
    from backend.utils.history import get_history
    return JSONResponse(get_history())


@app.get("/", tags=["Utility"], summary="Serve frontend application", include_in_schema=False)
async def serve_frontend():
    """Serve the main HTML frontend."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return JSONResponse(
        {"message": "Frontend not found. Visit /docs for the API interface."},
        status_code=200,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  DEVELOPMENT SERVER ENTRY-POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
