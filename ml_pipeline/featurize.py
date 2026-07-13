"""
featurize.py — Phase 2: Feature Engineering

Reads the chemical formulas from SQLite (`data/bandgap.db`),
generates Magpie composition features using matminer,
and saves the featurized dataset to `data/features.parquet`.
Also exports the exact feature column list to `ml_models/feature_columns.json`.

Usage:
    python -m ml_pipeline.featurize
"""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from matminer.featurizers.composition import ElementProperty  # type: ignore
from pymatgen.core import Composition  # type: ignore

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matminer")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "bandgap.db"
FEATURES_PATH = DATA_DIR / "features.parquet"
FEATURE_COLS_PATH = PROJECT_ROOT / "ml_models" / "feature_columns.json"

# ---------------------------------------------------------------------------
# Featurization Flow
# ---------------------------------------------------------------------------


def load_raw_data(db_path: Path) -> pd.DataFrame:
    """Load formula and band gap data from SQLite."""
    if not db_path.exists():
        print(f"❌  Database not found at {db_path}.")
        print("   Run 'make fetch' first to populate the training data.")
        sys.exit(1)

    print(f"📖  Reading raw data from {db_path} …")
    conn = sqlite3.connect(str(db_path))
    query = "SELECT material_id, formula, band_gap_ev FROM training_data"
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f"📋  Loaded {len(df)} rows.")
    return df


def parse_compositions(df: pd.DataFrame) -> pd.DataFrame:
    """Convert chemical formula strings to pymatgen Composition objects."""
    print("🧪  Parsing chemical formulas with pymatgen …")
    comps = []
    valid_indices = []

    for idx, formula in zip(df.index, df["formula"]):
        try:
            comps.append(Composition(formula))
            valid_indices.append(idx)
        except Exception as e:
            # Skip invalid compositions
            print(f"⚠️  Skipping invalid composition '{formula}': {e}")

    df_valid = df.loc[valid_indices].copy()
    df_valid["composition"] = comps
    print(f"✅  Parsed {len(df_valid)} valid compositions.")
    return df_valid


def featurize_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Compute Magpie composition features using matminer."""
    print("⚡  Generating Magpie composition features (this might take a minute) …")
    
    # Initialize the Magpie element property featurizer
    # Generates ~132 features representing chemistry statistics (mean, range, dev, etc.)
    ep = ElementProperty.from_preset("magpie")
    
    # Featurize the dataframe in-place
    df_features = ep.featurize_dataframe(df, col_id="composition", ignore_errors=True)
    
    # Identify which columns were added by the featurizer
    feature_cols = ep.feature_labels()
    
    # Drop rows that failed to featurize (they will have NaN across all feature columns)
    initial_len = len(df_features)
    df_features = df_features.dropna(subset=feature_cols)
    dropped = initial_len - len(df_features)
    
    if dropped > 0:
        print(f"⚠️  Dropped {dropped} rows due to featurization failures.")

    # Drop the temporary composition object column
    if "composition" in df_features.columns:
        df_features = df_features.drop(columns=["composition"])
        
    print(f"✅  Featurization complete. Shape: {df_features.shape}")
    return df_features, feature_cols


def main() -> None:
    # 1. Load data
    df = load_raw_data(DB_PATH)
    if len(df) == 0:
        print("❌  No training data found in SQLite table. Run 'make fetch' first.")
        sys.exit(1)

    # 2. Parse compositions
    df_parsed = parse_compositions(df)

    # 3. Generate features
    df_featurized, feature_cols = featurize_data(df_parsed)

    # 4. Save results
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FEATURE_COLS_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"💾  Saving features to {FEATURES_PATH} …")
    df_featurized.to_parquet(FEATURES_PATH, index=False)

    print(f"💾  Saving feature column names to {FEATURE_COLS_PATH} …")
    with open(FEATURE_COLS_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)

    print("🏁  Phase 2 complete — features engineered successfully!")


if __name__ == "__main__":
    main()
