"""
train.py — Phase 3a: Model Training

Loads the featurized dataset from `data/features.parquet`,
splits it 80/20 into train/test sets,
trains a Random Forest Regressor, and serializes the model
along with evaluation metrics.

Usage:
    python -m ml_pipeline.train
"""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
import mlflow
from mlflow.models import infer_signature
from mlflow.sklearn import log_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FEATURES_PATH = DATA_DIR / "features.parquet"
FEATURE_COLS_PATH = PROJECT_ROOT / "ml_models" / "feature_columns.json"
MODEL_PATH = PROJECT_ROOT / "ml_models" / "random_forest_bandgap.joblib"
SPLIT_INFO_PATH = DATA_DIR / "split_info.json"

# Hyperparameters (from implementation plan)
N_ESTIMATORS = 200
RANDOM_STATE = 42
TEST_SIZE = 0.20

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def load_features(
    features_path: Path, feature_cols_path: Path
) -> Tuple[pd.DataFrame, list]:
    """Load the featurized dataset and feature column names."""
    if not features_path.exists():
        print(f"❌  Feature file not found at {features_path}.")
        print("   Run 'make featurize' first.")
        sys.exit(1)

    print(f"📖  Loading features from {features_path} …")
    df = pd.read_parquet(features_path)

    with open(feature_cols_path, "r") as f:
        feature_cols = json.load(f)

    print(f"📋  Loaded {len(df)} rows with {len(feature_cols)} features.")
    return df, feature_cols


def split_data(
    df: pd.DataFrame, feature_cols: list, test_size: float, random_state: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict]:
    """Split data into train/test sets."""
    X = df[feature_cols].values
    y = df["band_gap_ev"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    split_info = {
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_size": test_size,
        "random_state": random_state,
        "n_features": len(feature_cols),
    }

    print(f"✂️  Split: {split_info['train_samples']} train / {split_info['test_samples']} test")
    return X_train, X_test, y_train, y_test, split_info


def train_model(
    X_train: np.ndarray, y_train: np.ndarray
) -> RandomForestRegressor:
    """Train a Random Forest Regressor."""
    print(f"🌲  Training RandomForestRegressor(n_estimators={N_ESTIMATORS}, random_state={RANDOM_STATE}) …")

    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Use all CPU cores
    )
    model.fit(X_train, y_train)

    print(f"✅  Training complete.")
    return model


def save_artifacts(
    model: RandomForestRegressor,
    split_info: Dict,
    model_path: Path,
    split_info_path: Path,
) -> None:
    """Serialize the trained model and split metadata."""
    model_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"💾  Saving model to {model_path} …")
    joblib.dump(model, model_path)

    print(f"💾  Saving split info to {split_info_path} …")
    with open(split_info_path, "w") as f:
        json.dump(split_info, f, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # 1. Load features
    df, feature_cols = load_features(FEATURES_PATH, FEATURE_COLS_PATH)

    # 2. Split data
    X_train, X_test, y_train, y_test, split_info = split_data(
        df, feature_cols, TEST_SIZE, RANDOM_STATE
    )

    # 3. Train model with MLflow tracking
    mlflow.set_experiment("Band_Gap_Prediction")
    with mlflow.start_run():
        mlflow.log_params({
            "n_estimators": N_ESTIMATORS,
            "random_state": RANDOM_STATE,
            "test_size": TEST_SIZE
        })
        
        model = train_model(X_train, y_train)
        
        # Evaluate on test set for MLflow
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = r2_score(y_test, y_pred)
        
        mlflow.log_metrics({
            "mae_ev": mae,
            "rmse_ev": rmse,
            "r2_score": r2
        })
        
        signature = infer_signature(X_train, model.predict(X_train))
        
        log_model(
            sk_model=model, 
            name="random_forest_bandgap",
            signature=signature,
            input_example=X_train[:5]
        )

    # 4. Save model and split info
    save_artifacts(model, split_info, MODEL_PATH, SPLIT_INFO_PATH)

    # 5. Save test set for evaluation script
    test_data_path = DATA_DIR / "test_set.npz"
    print(f"💾  Saving test set to {test_data_path} …")
    np.savez(test_data_path, X_test=X_test, y_test=y_test)

    print("🏁  Phase 3a complete — model trained and saved!")


if __name__ == "__main__":
    main()
