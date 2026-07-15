# ⚛️ Quantum Gap: Band Gap Prediction Dashboard

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

> A modern, glassmorphic web application for predicting the band gap energy of materials based on their chemical formulas using machine learning.

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
- **📚 Educational Insights**: Detailed scientific explanations on the physical implications of different band gaps.
- **⚙️ Simulation Process**: Step-by-step visual demonstration of the calculation and featurization process.
- **🕒 Prediction History**: A sleek history table to quickly reference recent predictions.
- **🎨 Modern UI/UX**: Clean, responsive, and professional glassmorphic design.
- **🌐 Localization**: Fully translated interface and scientific terminology for Vietnamese users.

---

## 🛠 Tech Stack

### Frontend
- **[React 18](https://react.dev/)** - UI Library
- **[TypeScript](https://www.typescriptlang.org/)** - Static Typing
- **[Vite](https://vitejs.dev/)** - Build Tool
- **Vanilla CSS** - Styling (Glassmorphism design)

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Web Framework (Python)
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI Server

### Machine Learning
- **[scikit-learn](https://scikit-learn.org/)** - Random Forest classification model
- **[pymatgen](https://pymatgen.org/)** & **[matminer](https://hackingmaterials.lbl.gov/matminer/)** - Chemical formula parsing and Magpie descriptor featurization

---

## 📂 Directory Structure

```text
.
├── backend/                # FastAPI server and ML pipeline
│   ├── main.py             # API endpoints
│   └── models/             # Contains the trained rf_model.joblib
├── frontend/               # React Vite application
│   ├── src/                # Components, CSS, and application logic
│   └── index.html          # Entry point
└── data/                   # Datasets and SQLite DB
```

---

## 🚀 Getting Started

Follow these instructions to set up the project locally.

> ⚠️ **Important**: All commands must be run from the **project root** directory (`Band_Gap_Prediction_From_Chemical_Formula/`), unless otherwise specified.

### Prerequisites

Ensure you have the following installed on your machine:
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://www.python.org/) 3.9+
- pip (Python package installer)

### Installation

#### 1. Clone the repository and navigate to the project root

```bash
git clone <your-repo-url>
cd Band_Gap_Prediction_From_Chemical_Formula
```

#### 2. Backend Setup

From the **project root**, create and activate the virtual environment, then install dependencies:

```bash
# Create a virtual environment in the project root
python -m venv .venv

# Activate it:
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### 3. Frontend Setup

From the **project root**, install npm packages:

```bash
cd frontend && npm install && cd ..
```

---

## 💻 Usage

To run the application locally, you need **two separate terminal windows**, both opened at the **project root**.

### Option A — Makefile (Quickest)

```bash
# Terminal 1 — start the backend
make serve

# Terminal 2 — start the frontend
make dev
```

### Option B — Manual Commands

#### Terminal 1 — Backend Server

```bash
# From the project root, activate the virtual environment
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows

# Start the FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
_The API will be available at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`._

#### Terminal 2 — Frontend Server

```bash
# Navigate into the frontend folder
cd frontend

# Start the Vite dev server
npm run dev
```
_The app will be available at `http://localhost:5173`._

---

## 🧠 Project Architecture & How it Works

1. **User Input**: The user enters a chemical formula (e.g., `NaCl`, `SiO2`) into the React interface.
2. **API Request**: The frontend transmits the formula to the FastAPI backend via a POST request.
3. **Featurization**: 
   - The backend utilizes `pymatgen` to parse the chemical composition.
   - It then uses `matminer` to extract Magpie descriptors (elemental properties based on the formula).
4. **Prediction**: The extracted features are fed into a pre-trained `scikit-learn` Random Forest model, classifying the band gap as "High" or "Low".
5. **Response & Visualization**: The result is returned to the frontend and displayed with step-by-step loading animations, followed by scientific insights.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
