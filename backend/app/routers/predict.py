"""
predict.py — Router: POST /predict

Validates a chemical formula with pymatgen, featurizes it,
predicts the band gap, saves the query to SQLite, and returns the result.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.featurizer import CompositionFeaturizer
from backend.app.services.predictor import BandGapPredictor
from backend.app.worker import predict_band_gap_task, celery_app
from celery.result import AsyncResult

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


class AsyncPredictResponse(BaseModel):
    task_id: str


class BatchPredictRequest(BaseModel):
    formulas: List[str] = Field(..., examples=[["GaAs", "NaCl", "Fe2O3"]], description="List of chemical formulas")


class BatchPredictResponse(BaseModel):
    task_ids: List[str]


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


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


@router.post("/predict/async", response_model=AsyncPredictResponse)
async def predict_band_gap_async(request: PredictRequest) -> AsyncPredictResponse:
    """
    Dispatch a prediction task to the Celery worker.
    Returns a task_id immediately.
    """
    task = predict_band_gap_task.delay(request.formula.strip())
    return AsyncPredictResponse(task_id=task.id)


@router.post("/predict/batch", response_model=BatchPredictResponse)
async def predict_band_gap_batch(request: BatchPredictRequest) -> BatchPredictResponse:
    """
    Dispatch multiple prediction tasks to Celery.
    Returns a list of task_ids.
    """
    task_ids = []
    for formula in request.formulas:
        if formula.strip():
            task = predict_band_gap_task.delay(formula.strip())
            task_ids.append(task.id)
    return BatchPredictResponse(task_ids=task_ids)


@router.get("/predict/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Check the status of an async prediction task.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    response = TaskStatusResponse(
        task_id=task_id,
        status=task_result.status
    )
    if task_result.status == "SUCCESS":
        response.result = task_result.result
    elif task_result.status == "FAILURE":
        response.error = str(task_result.result)
    
    return response
