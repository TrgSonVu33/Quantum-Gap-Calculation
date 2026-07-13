"""
predictor.py — Backend Service: Band Gap Predictor

Loads the serialized Random Forest model and provides prediction
with band gap classification logic.
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "ml_models" / "random_forest_bandgap.joblib"


class BandGapPredictor:
    """
    Wraps the trained Random Forest model for single-sample prediction.

    Initialised once at server startup and reused across all requests.
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        self.model: RandomForestRegressor = joblib.load(model_path)

    def predict(self, feature_vector: np.ndarray) -> float:
        """
        Predict the band gap for a single feature vector.

        Args:
            feature_vector: 1D array of shape (n_features,).

        Returns:
            Predicted band gap in eV (float).
        """
        # Reshape to 2D for sklearn: (1, n_features)
        X = feature_vector.reshape(1, -1)
        prediction = self.model.predict(X)[0]
        return round(float(prediction), 4)

    @staticmethod
    def classify(band_gap_ev: float) -> str:
        """
        Classify a band gap value into material type.

        Classification rule (from implementation plan):
            band_gap == 0       → Metal
            0 < band_gap ≤ 3.0  → Semiconductor
            band_gap > 3.0      → Insulator

        Args:
            band_gap_ev: Predicted band gap in eV.

        Returns:
            One of 'Metal', 'Semiconductor', or 'Insulator'.
        """
        if band_gap_ev <= 0:
            return "Metal"
        elif band_gap_ev <= 3.0:
            return "Semiconductor"
        else:
            return "Insulator"
