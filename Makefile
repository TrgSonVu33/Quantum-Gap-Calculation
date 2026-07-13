# Band Gap Prediction — Makefile
# Convenience targets for the full pipeline.

.PHONY: fetch featurize train serve dev install-ml install-backend install-frontend

# ---- ML Pipeline ----

install-ml:
	.venv/bin/pip install -r ml_pipeline/requirements.txt

fetch:
	.venv/bin/python -m ml_pipeline.fetch_data

featurize:
	.venv/bin/python -m ml_pipeline.featurize

train:
	.venv/bin/python -m ml_pipeline.train

evaluate:
	.venv/bin/python -m ml_pipeline.evaluate

pipeline: fetch featurize train evaluate
	@echo "✅  Full ML pipeline complete."

# ---- Backend ----

install-backend:
	.venv/bin/pip install -r backend/requirements.txt

serve:
	.venv/bin/uvicorn backend.app.main:app --reload --port 8000

# ---- Frontend ----

install-frontend:
	cd frontend && npm install

dev:
	cd frontend && npm run dev

# ---- All ----

install: install-ml install-backend install-frontend
	@echo "✅  All dependencies installed."
