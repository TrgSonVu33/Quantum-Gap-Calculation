"""
main.py — FastAPI Application Entry Point

Band Gap Prediction API.
Loads the ML model and featurizer once at startup via the lifespan context,
configures CORS, and mounts all routers under /api/v1.

Usage:
    uvicorn backend.app.main:app --reload --port 8000
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matminer")

# Apply hotfixes before importing any mp-api / emmet dependencies
# (same patches used in fetch_data.py)
try:
    import pymatgen.symmetry.analyzer as psa
    if not hasattr(psa, "SymmetryUndeterminedError"):
        psa.SymmetryUndeterminedError = getattr(psa, "SymmetryUndetermined", ValueError)
except ImportError:
    pass

try:
    import emmet.core.phonon as ecp
    if not hasattr(ecp, "PhononBS"):
        ecp.PhononBS = getattr(ecp, "PhononBandStructure", None)
    if not hasattr(ecp, "PhononDOS"):
        ecp.PhononDOS = getattr(ecp, "PhononDos", None)
except ImportError:
    pass

from backend.app.routers import history, predict
from backend.app.services.featurizer import CompositionFeaturizer
from backend.app.services.predictor import BandGapPredictor

# ---------------------------------------------------------------------------
# Lifespan — load model & featurizer once at startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Load heavy ML artifacts once when the server starts."""
    print("🚀  Loading ML model and featurizer …")

    try:
        featurizer = CompositionFeaturizer()
        predictor_svc = BandGapPredictor()
    except Exception as e:
        print(f"❌  Failed to load ML artifacts: {e}")
        sys.exit(1)

    # Inject into the predict router module
    predict.featurizer = featurizer
    predict.predictor = predictor_svc

    print("✅  Model and featurizer loaded successfully.")
    print(f"   Model: {type(predictor_svc.model).__name__} ({predictor_svc.model.n_estimators} estimators)")
    print(f"   Features: {len(featurizer.feature_columns)} Magpie columns")

    yield  # Server is running

    print("👋  Shutting down …")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Band Gap Prediction API",
    description="Predict the band gap of inorganic materials from their chemical formula.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the React frontend (typically on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive for local dev; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers under /api/v1
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Lightweight liveness check."""
    model_loaded = predict.predictor is not None
    return {"status": "healthy", "model_loaded": model_loaded}
