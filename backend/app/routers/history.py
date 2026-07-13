"""
history.py — Router: GET /history

Retrieves past prediction queries from the user_queries table,
sorted by newest first, with pagination support.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "bandgap.db"

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class QueryRecord(BaseModel):
    id: int
    formula: str
    predicted_band_gap_ev: float
    classification: str
    created_at: str


class HistoryResponse(BaseModel):
    total: int
    queries: List[QueryRecord]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=50, ge=1, le=500, description="Max rows to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
) -> HistoryResponse:
    """
    Retrieve past prediction queries, newest first.

    Supports pagination via `limit` and `offset` query parameters.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Get total count
    (total,) = conn.execute("SELECT COUNT(*) FROM user_queries").fetchone()

    # Fetch paginated results, newest first
    rows = conn.execute(
        """
        SELECT id, formula, predicted_band_gap_ev, classification, created_at
        FROM user_queries
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()

    conn.close()

    queries = [
        QueryRecord(
            id=row["id"],
            formula=row["formula"],
            predicted_band_gap_ev=row["predicted_band_gap_ev"],
            classification=row["classification"],
            created_at=row["created_at"],
        )
        for row in rows
    ]

    return HistoryResponse(total=total, queries=queries)
