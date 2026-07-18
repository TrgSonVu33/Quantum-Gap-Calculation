# ──────────────────────────────────────────────────────────────────────────────
# Backend Dockerfile — Band Gap Prediction API
#
# Python 3.10 + FastAPI/Uvicorn
# Serves the ML prediction API on port 8000.
#
# Build context: ./backend (via docker-compose)
# Volumes: data/ and ml_models/ are mounted at runtime.
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# System dependencies required by pymatgen, matminer, and numpy/scipy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Install Python dependencies ──────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy application source ─────────────────────────────────────────────────
# Build context is ./backend, so COPY . copies backend/* into /app/backend/
COPY . /app/backend/

# Create empty directories for volume mount points
RUN mkdir -p /app/data /app/ml_models

# Set PYTHONPATH so `from backend.app.…` imports resolve correctly
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
