"""
evaluate.py — Phase 3b: Model Evaluation

Loads the trained model and test set, computes regression metrics
(MAE, RMSE, R²), extracts feature importances, and generates
a model card with all results.

Usage:
    python -m ml_pipeline.evaluate
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "ml_models"

MODEL_PATH = MODELS_DIR / "random_forest_bandgap.joblib"
TEST_SET_PATH = DATA_DIR / "test_set.npz"
FEATURE_COLS_PATH = MODELS_DIR / "feature_columns.json"
METRICS_PATH = MODELS_DIR / "metrics.json"
MODEL_CARD_PATH = MODELS_DIR / "model_card.md"

# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def load_artifacts() -> Tuple:
    """Load the trained model, test data, and feature column names."""
    for path, name in [
        (MODEL_PATH, "Model"),
        (TEST_SET_PATH, "Test set"),
        (FEATURE_COLS_PATH, "Feature columns"),
    ]:
        if not path.exists():
            print(f"❌  {name} not found at {path}.")
            print("   Run 'make train' first.")
            sys.exit(1)

    print("📖  Loading model, test set, and feature columns …")
    model = joblib.load(MODEL_PATH)
    test_data = np.load(TEST_SET_PATH)
    X_test = test_data["X_test"]
    y_test = test_data["y_test"]

    with open(FEATURE_COLS_PATH, "r") as f:
        feature_cols = json.load(f)

    print(f"   Model: {type(model).__name__} ({model.n_estimators} estimators)")
    print(f"   Test set: {X_test.shape[0]} samples × {X_test.shape[1]} features")
    return model, X_test, y_test, feature_cols


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Compute MAE, RMSE, and R² regression metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)

    metrics = {
        "mae_ev": round(mae, 4),
        "rmse_ev": round(rmse, 4),
        "r2_score": round(r2, 4),
        "n_test_samples": len(y_true),
    }

    print("\n📊  Evaluation Metrics")
    print(f"    MAE  : {metrics['mae_ev']:.4f} eV")
    print(f"    RMSE : {metrics['rmse_ev']:.4f} eV")
    print(f"    R²   : {metrics['r2_score']:.4f}")
    return metrics


def get_feature_importances(
    model, feature_cols: List[str], top_n: int = 20
) -> List[Dict]:
    """Extract and rank feature importances from the trained model."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]

    top_features = []
    for rank, idx in enumerate(indices, 1):
        top_features.append(
            {
                "rank": rank,
                "feature": feature_cols[idx],
                "importance": round(float(importances[idx]), 6),
            }
        )

    print(f"\n🏆  Top {top_n} Feature Importances")
    for feat in top_features:
        bar = "█" * int(feat["importance"] * 100)
        print(f"    {feat['rank']:2d}. {feat['feature']:<45s} {feat['importance']:.4f}  {bar}")

    return top_features


def generate_model_card(
    metrics: Dict, top_features: List[Dict], model_card_path: Path
) -> None:
    """Generate a markdown model card with metrics and feature importances."""
    lines = [
        "# Model Card — Band Gap Predictor (Random Forest)",
        "",
        "## Model Details",
        "",
        "| Property | Value |",
        "|---|---|",
        "| Algorithm | `RandomForestRegressor` |",
        "| Estimators | 200 |",
        "| Random State | 42 |",
        "| Training Split | 80% train / 20% test |",
        f"| Test Samples | {metrics['n_test_samples']} |",
        "",
        "## Performance Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **MAE** | {metrics['mae_ev']:.4f} eV |",
        f"| **RMSE** | {metrics['rmse_ev']:.4f} eV |",
        f"| **R²** | {metrics['r2_score']:.4f} |",
        "",
        "## Top 20 Feature Importances",
        "",
        "| Rank | Feature | Importance |",
        "|---|---|---|",
    ]

    for feat in top_features:
        lines.append(f"| {feat['rank']} | `{feat['feature']}` | {feat['importance']:.4f} |")

    lines.extend([
        "",
        "## Dataset",
        "",
        "- **Source**: Materials Project (stable inorganic materials, `is_stable=True`)",
        "- **Total samples**: ~5,000",
        "- **Target variable**: Band gap (eV), DFT-computed",
        "- **Features**: 132 Magpie composition descriptors via `matminer`",
        "",
        "## Limitations",
        "",
        "- Trained on DFT-computed band gaps, which systematically underestimate experimental values.",
        "- Composition-only features — does not account for crystal structure or polymorphism.",
        "- Limited to inorganic materials present in the Materials Project database.",
        "",
    ])

    model_card_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_card_path, "w") as f:
        f.write("\n".join(lines))

    print(f"\n📄  Model card saved to {model_card_path}")


def save_metrics(metrics: Dict, top_features: List[Dict], metrics_path: Path) -> None:
    """Save metrics and top features to a JSON file."""
    output = {
        "metrics": metrics,
        "top_features": top_features,
    }
    with open(metrics_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"💾  Metrics saved to {metrics_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # 1. Load artifacts
    model, X_test, y_test, feature_cols = load_artifacts()

    # 2. Predict
    print("\n🔮  Running predictions on test set …")
    y_pred = model.predict(X_test)

    # 3. Compute metrics
    metrics = compute_metrics(y_test, y_pred)

    # 4. Feature importances
    top_features = get_feature_importances(model, feature_cols, top_n=20)

    # 5. Save outputs
    save_metrics(metrics, top_features, METRICS_PATH)
    generate_model_card(metrics, top_features, MODEL_CARD_PATH)

    print("\n🏁  Phase 3b complete — evaluation finished!")


if __name__ == "__main__":
    main()
