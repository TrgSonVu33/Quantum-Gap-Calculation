"""
featurizer.py — Backend Service: Composition Featurizer

Reuses the same matminer Magpie featurization pipeline used during training
to convert a single chemical formula string into a feature vector.
"""

import json
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from matminer.featurizers.composition import ElementProperty
from pymatgen.core import Composition

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
FEATURE_COLS_PATH = PROJECT_ROOT / "ml_models" / "feature_columns.json"


class CompositionFeaturizer:
    """
    Wraps matminer's ElementProperty featurizer for single-formula inference.

    Initialised once at server startup and reused across all requests.
    """

    def __init__(self, feature_cols_path: Path = FEATURE_COLS_PATH):
        # Load the exact feature column order used during training
        with open(feature_cols_path, "r") as f:
            self.feature_columns: List[str] = json.load(f)

        # Initialise the same Magpie preset used in training
        self.featurizer = ElementProperty.from_preset("magpie")

    def validate_formula(self, formula: str) -> Composition:
        """
        Parse and validate a chemical formula string.

        Args:
            formula: A chemical formula string (e.g., "GaAs", "NaCl").

        Returns:
            A pymatgen Composition object.

        Raises:
            ValueError: If the formula cannot be parsed.
        """
        try:
            comp = Composition(formula)
            # Sanity check: must contain at least one element
            if len(comp.elements) == 0:
                raise ValueError("Formula contains no elements.")
            return comp
        except Exception as e:
            raise ValueError(
                f"Invalid chemical formula: '{formula}' could not be parsed by pymatgen. {e}"
            )

    def featurize(self, formula: str) -> np.ndarray:
        """
        Convert a chemical formula into a numerical feature vector.

        Args:
            formula: A chemical formula string.

        Returns:
            A 1D numpy array of shape (n_features,) matching the training columns.

        Raises:
            ValueError: If the formula is invalid or featurization fails.
        """
        comp = self.validate_formula(formula)

        try:
            features = self.featurizer.featurize(comp)
        except Exception as e:
            raise ValueError(
                f"Featurization failed for '{formula}': {e}"
            )

        feature_array = np.array(features, dtype=np.float64)

        # Verify we got the expected number of features
        if len(feature_array) != len(self.feature_columns):
            raise ValueError(
                f"Feature count mismatch: expected {len(self.feature_columns)}, "
                f"got {len(feature_array)}."
            )

        return feature_array
