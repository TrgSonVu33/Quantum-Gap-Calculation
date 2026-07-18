"""
worker.py — Celery Application & Async Prediction Task

Configures Celery with a Redis broker/backend (from env vars) and defines
the `predict_band_gap_task` that offloads the heavy featurization + ML
prediction to a background worker process.

The featurizer and predictor are lazy-loaded once per worker process
to avoid re-initializing on every task invocation.
"""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from celery import Celery

# ---------------------------------------------------------------------------
# Celery App Configuration
# ---------------------------------------------------------------------------

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "bandgap_worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Keep results for 24 hours
    result_expires=86400,
    # Prefetch only 1 task at a time (heavy ML workload)
    worker_prefetch_multiplier=1,
)

# ---------------------------------------------------------------------------
# Lazy-loaded ML artifacts (initialized once per worker process)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "bandgap.db"

_featurizer = None
_predictor = None


def _get_featurizer():
    """Lazy-load the CompositionFeaturizer (once per worker process)."""
    global _featurizer
    if _featurizer is None:
        from backend.app.services.featurizer import CompositionFeaturizer
        _featurizer = CompositionFeaturizer()
    return _featurizer


def _get_predictor():
    """Lazy-load the BandGapPredictor (once per worker process)."""
    global _predictor
    if _predictor is None:
        from backend.app.services.predictor import BandGapPredictor
        _predictor = BandGapPredictor()
    return _predictor


# ---------------------------------------------------------------------------
# Celery Tasks
# ---------------------------------------------------------------------------


@celery_app.task(name="predict_band_gap", bind=True, max_retries=2)
def predict_band_gap_task(self, formula: str) -> dict:
    """
    Async prediction task: featurize → predict → classify → save to DB.

    Args:
        formula: Chemical formula string (e.g., "GaAs", "NaCl").

    Returns:
        dict with formula, predicted_band_gap_ev, classification, timestamp.
    """
    try:
        featurizer = _get_featurizer()
        predictor = _get_predictor()

        # 1. Featurize
        feature_vector = featurizer.featurize(formula.strip())

        # 2. Predict & classify
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
                (formula.strip(), band_gap, classification),
            )
            conn.commit()
            conn.close()
        except Exception:
            # Don't fail the prediction if DB write fails
            pass

        return {
            "formula": formula.strip(),
            "predicted_band_gap_ev": band_gap,
            "classification": classification,
            "timestamp": timestamp,
        }

    except ValueError as e:
        # Validation / featurization errors — don't retry
        raise ValueError(str(e))
    except Exception as exc:
        # Transient errors — retry with exponential backoff
        raise self.retry(exc=exc, countdown=5 * (self.request.retries + 1))
