# Quantum Gap: Band Gap Prediction Dashboard

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)

> A modern, glassmorphic web application for predicting the band gap energy of materials based on their chemical formulas using machine learning, built with a full-stack MLOps and Dockerized architecture.

<br/>

<div align="center">
  <img src="frontend/src/assets/Homepage.png" alt="Quantum Gap Dashboard Screenshot" width="800" style="border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
</div>

<br/>

## 📋 Table of Contents
- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Directory Structure](#-directory-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Project Architecture](#-project-architecture--how-it-works)
- [License](#-license)

---

## 📖 About the Project

**Quantum Gap** is an educational and predictive tool designed for materials science. It predicts whether a material possesses a **High** or **Low** band gap energy (_Vùng cấm năng lượng_) directly from its chemical formula. 

Powered by a Random Forest machine learning model trained on Materials Project data, this application serves as both a predictive utility and an educational platform, fully localized in Vietnamese.

---

## ✨ Features

- **🎯 Accurate Predictions**: Instantly classify the band gap (High/Low) from a chemical formula.
- **🐳 Dockerized Deployment**: Run the entire stack seamlessly with a single Docker Compose command.
- **⚡ Background Processing**: Scalable batch predictions using Celery and Redis.
- **🧬 3D Visualization**: Interactive 3D molecular viewer for predicted chemical structures.
- **📊 MLOps Integration**: Full experiment tracking and model registry with MLflow.
- **📚 Educational Insights**: Detailed scientific explanations on the physical implications of different band gaps.
- **🕒 Prediction History**: A sleek history table to quickly reference recent predictions.
- **🎨 Modern UI/UX**: Clean, responsive, and professional glassmorphic design.

---

## 🛠 Tech Stack

### Frontend
- **[React 18](https://react.dev/)** - UI Library
- **[TypeScript](https://www.typescriptlang.org/)** - Static Typing
- **[Vite](https://vitejs.dev/)** - Build Tool
- **Vanilla CSS** - Styling (Glassmorphism design)
- **3Dmol.js** - Interactive 3D chemical structure visualization

### Backend & Infrastructure
- **[FastAPI](https://fastapi.tiangolo.com/)** - Web Framework (Python)
- **[Celery](https://docs.celeryq.dev/) & [Redis](https://redis.io/)** - Distributed task queue for asynchronous and batch processing
- **[Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)** - Containerization and orchestration
- **[Nginx](https://www.nginx.com/)** - Web server / Reverse proxy for production

### Machine Learning & MLOps
- **[scikit-learn](https://scikit-learn.org/)** - Random Forest classification model
- **[MLflow](https://mlflow.org/)** - ML lifecycle, metrics, and model experiment tracking
- **[pymatgen](https://pymatgen.org/)** & **[matminer](https://hackingmaterials.lbl.gov/matminer/)** - Chemical formula parsing and Magpie descriptor featurization

---

## 📂 Directory Structure

```text
.
├── backend/                # FastAPI server, Celery worker, and ML pipeline dependencies
│   ├── app/                # Main application code (routers, worker.py)
│   ├── Dockerfile          # Backend container definition
│   └── requirements.txt    # Python dependencies
├── frontend/               # React Vite application
│   ├── src/                # Components (ResultCard, PredictionForm)
│   ├── Dockerfile          # Frontend builder container
│   └── nginx.conf          # Nginx configuration for production
├── ml_models/              # Trained models and metrics
├── mlruns/                 # MLflow experiment tracking data
├── ml_pipeline/            # Data fetching and model training scripts
├── docker-compose.yml      # Orchestrates backend, frontend, redis, and Celery worker
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

Ensure you have the following installed on your machine:
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- *(Optional for manual setup)* [Node.js](https://nodejs.org/) (v18+) and [Python](https://www.python.org/) 3.9+

### Quick Start with Docker (Recommended)

1. **Clone the repository and navigate to the project root:**
   ```bash
   git clone <your-repo-url>
   cd Band_Gap_Prediction_From_Chemical_Formula
   ```

2. **Start the entire application stack using Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

   This spins up:
   - The React frontend (served by Nginx) at `http://localhost:80`
   - The FastAPI backend at `http://localhost:8000`
   - A Redis broker
   - A Celery worker for processing asynchronous predictions

---

## 💻 Usage

### Docker Development

If you are using Docker, the application is ready once `docker-compose up -d` finishes.

- **Frontend Interface:** [http://localhost](http://localhost)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

To view the logs of your services:
```bash
docker-compose logs -f
```

To stop the services:
```bash
docker-compose down
```

### Manual Development / Local Setup

If you prefer to run the project without Docker:

1. **Backend Server** (Terminal 1)
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   uvicorn backend.app.main:app --reload --port 8000
   ```
2. **Celery Worker** (Terminal 2 - requires local Redis instance running)
   ```bash
   celery -A backend.app.worker worker --loglevel=info
   ```
3. **Frontend Server** (Terminal 3)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🧠 Project Architecture & How it Works

1. **User Input**: The user enters a chemical formula (e.g., `NaCl`, `SiO2`) or uploads a batch of formulas into the React interface.
2. **API Request**: The frontend transmits the formula to the FastAPI backend.
3. **Task Queueing**: For scalability, processing is delegated to a background **Celery Worker** orchestrated by **Redis**.
4. **Featurization**: 
   - The worker utilizes `pymatgen` to parse the chemical composition.
   - It uses `matminer` to extract Magpie descriptors (elemental properties based on the formula).
5. **Prediction**: Features are evaluated by a pre-trained `scikit-learn` Random Forest model (tracked by **MLflow**), classifying the band gap as "High" or "Low".
6. **Response & Visualization**: The result is returned asynchronously and displayed on the UI alongside an interactive 3D molecule model.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
