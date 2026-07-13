"""
predict.py — Router: POST /predict

Validates a chemical formula with pymatgen, featurizes it,
predicts the band gap, saves the query to SQLite, and returns the result.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.featurizer import CompositionFeaturizer
from backend.app.services.predictor import BandGapPredictor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "bandgap.db"

router = APIRouter()

# These will be set by the lifespan handler in main.py
featurizer: CompositionFeaturizer = None  # type: ignore
predictor: BandGapPredictor = None  # type: ignore


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PredictRequest(BaseModel):
    formula: str = Field(
        ...,
        min_length=1,
        max_length=200,
        examples=["GaAs", "NaCl", "Fe2O3"],
        description="Chemical formula string",
    )


class PredictResponse(BaseModel):
    formula: str
    predicted_band_gap_ev: float
    classification: str
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/predict", response_model=PredictResponse)
async def predict_band_gap(request: PredictRequest) -> PredictResponse:
    """
    Predict the band gap for a given chemical formula.

    1. Validates the formula using pymatgen.
    2. Generates Magpie composition features.
    3. Runs prediction through the Random Forest model.
    4. Classifies the result (Metal / Semiconductor / Insulator).
    5. Saves the query to the user_queries table.
    """
    formula = request.formula.strip()

    # 1. Validate & featurize
    try:
        feature_vector = featurizer.featurize(formula)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 2. Predict
    band_gap = predictor.predict(feature_vector)
    classification = predictor.classify(band_gap)

    # 3. Timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # 4. Save to database
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            """
            INSERT INTO user_queries (formula, predicted_band_gap_ev, classification)
            VALUES (?, ?, ?)
            """,
            (formula, band_gap, classification),
        )
        conn.commit()
        conn.close()
    except Exception:
        # Don't fail the prediction if DB write fails — log and continue
        pass

    return PredictResponse(
        formula=formula,
        predicted_band_gap_ev=band_gap,
        classification=classification,
        timestamp=timestamp,
    )
