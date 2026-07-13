"""
fetch_data.py — Phase 1: Data Fetching & Storage

Fetches ~5,000 stable inorganic materials from the Materials Project API
and stores them in the local SQLite database (`data/bandgap.db`).

Usage:
    python -m ml_pipeline.fetch_data

Environment:
    MP_API_KEY must be set in .env or as an environment variable.
"""

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

# Apply hotfix for pymatgen symmetry analyzer version incompatibility
import pymatgen.symmetry.analyzer as psa
if not hasattr(psa, "SymmetryUndeterminedError"):
    psa.SymmetryUndeterminedError = getattr(psa, "SymmetryUndetermined", ValueError)

# Apply hotfix for emmet.core.phonon class name changes
import emmet.core.phonon as ecp
if not hasattr(ecp, "PhononBS"):
    ecp.PhononBS = getattr(ecp, "PhononBandStructure", None)
if not hasattr(ecp, "PhononDOS"):
    ecp.PhononDOS = getattr(ecp, "PhononDos", None)

# Apply hotfix for emmet.core.mpid Pydantic validation
try:
    import emmet.core.mpid as mpid
    from pydantic_core import core_schema
    from typing import Any
    def _patched_mpid_validate(cls, __input_value: Any, _: core_schema.ValidationInfo):
        return str(__input_value)
    mpid.MPID.validate = classmethod(_patched_mpid_validate)
except ImportError:
    pass

from dotenv import load_dotenv
from mp_api.client import MPRester

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "bandgap.db"

load_dotenv(PROJECT_ROOT / ".env")
MP_API_KEY = os.getenv("MP_API_KEY")

# How many materials to target (set to None for no cap)
MAX_MATERIALS = 5_000

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def init_db(db_path: Path) -> sqlite3.Connection:
    """Create the SQLite database and training_data table if they don't exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS training_data (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id  TEXT    UNIQUE NOT NULL,
            formula      TEXT    NOT NULL,
            band_gap_ev  REAL    NOT NULL,
            is_stable    INTEGER NOT NULL DEFAULT 1,
            fetched_at   TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_queries (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            formula                TEXT    NOT NULL,
            predicted_band_gap_ev  REAL    NOT NULL,
            classification         TEXT    NOT NULL,
            created_at             TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Materials Project fetcher
# ---------------------------------------------------------------------------


def fetch_materials(api_key: str, max_materials: Optional[int] = MAX_MATERIALS) -> List[Dict]:
    """
    Query the Materials Project for stable inorganic materials.

    Returns a list of dicts with keys: material_id, formula, band_gap_ev.
    """
    print(f"🔗  Connecting to Materials Project API …")

    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            is_stable=True,
            fields=["material_id", "formula_pretty", "band_gap"],
            num_chunks=None,
        )

    print(f"📦  Received {len(docs)} documents from MP.")

    records = []
    for doc in docs:
        # band_gap can be None for some entries — skip those
        if doc.band_gap is None:
            continue
        records.append(
            {
                "material_id": str(doc.material_id),
                "formula": doc.formula_pretty,
                "band_gap_ev": float(doc.band_gap),
            }
        )

    # If the user wants to cap the dataset size
    if max_materials and len(records) > max_materials:
        records = records[:max_materials]

    print(f"✅  Prepared {len(records)} records (after filtering nulls).")
    return records


# ---------------------------------------------------------------------------
# Insert into SQLite
# ---------------------------------------------------------------------------


def insert_records(conn: sqlite3.Connection, records: List[Dict]) -> int:
    """
    Insert fetched material records into the training_data table.

    Uses INSERT OR IGNORE to safely handle re-runs without duplicates.
    Returns the number of newly inserted rows.
    """
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        (r["material_id"], r["formula"], r["band_gap_ev"], 1, now)
        for r in records
    ]

    cursor = conn.executemany(
        """
        INSERT OR IGNORE INTO training_data
            (material_id, formula, band_gap_ev, is_stable, fetched_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    inserted = cursor.rowcount
    print(f"💾  Inserted {inserted} new rows into training_data.")
    return inserted


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate(conn: sqlite3.Connection) -> None:
    """Run basic sanity checks on the stored data."""
    (total,) = conn.execute("SELECT COUNT(*) FROM training_data").fetchone()
    (avg_bg,) = conn.execute("SELECT AVG(band_gap_ev) FROM training_data").fetchone()
    (min_bg,) = conn.execute("SELECT MIN(band_gap_ev) FROM training_data").fetchone()
    (max_bg,) = conn.execute("SELECT MAX(band_gap_ev) FROM training_data").fetchone()

    print("\n📊  Validation Summary")
    print(f"    Total records : {total}")
    print(f"    Band gap range: {min_bg:.3f} – {max_bg:.3f} eV")
    print(f"    Mean band gap : {avg_bg:.3f} eV")

    # Spot-check: look for Silicon (Si)
    row = conn.execute(
        "SELECT formula, band_gap_ev FROM training_data WHERE formula = 'Si'"
    ).fetchone()
    if row:
        print(f"    Spot-check Si  : {row[1]:.3f} eV (expected ~0.6–1.2 eV DFT)")
    else:
        print("    ⚠️  Si not found in dataset — check query filters.")

    assert total > 1000, f"Expected at least 1,000 records, got {total}"
    print("\n✅  Validation passed.\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not MP_API_KEY:
        print("❌  MP_API_KEY not set. Create a .env file with your key.")
        print("   → Register at https://next-gen.materialsproject.org")
        sys.exit(1)

    print(f"📂  Database path: {DB_PATH}")
    conn = init_db(DB_PATH)

    try:
        records = fetch_materials(MP_API_KEY)
        insert_records(conn, records)
        validate(conn)
    finally:
        conn.close()

    print("🏁  Phase 1 complete — data fetched and stored.")


if __name__ == "__main__":
    main()
