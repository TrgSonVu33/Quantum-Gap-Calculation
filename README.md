# Quantum Gap: Band Gap Prediction Dashboard

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

<br/>

<div align="center">
  <!-- TODO: Replace the 'assets/screenshot.png' path below with your actual screenshot image path/URL -->
  <img src="assets/Homepage.png" alt="Quantum Gap Dashboard Screenshot" width="800" style="border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
</div>

<br/>

## About the Project

**Quantum Gap** is a web application that predicts the band gap energy (_Vùng cấm năng lượng_) of materials based on their chemical formula. It utilizes a Random Forest machine learning model trained on Materials Project data to classify whether a given material has a High or Low band gap.

The application is designed with a modern glassmorphic UI, fully localized in Vietnamese, providing an intuitive and educational experience for users in materials science.

## Features

- **Accurate Predictions**: Predicts Band Gap (High/Low) directly from a chemical formula.
- **Educational Insights**: Provides scientific explanations detailing what High vs. Low band gap means and its implications for material properties.
- **Simulation Process**: Features a step-by-step calculation simulation to visually demonstrate the process behind the prediction.
- **Prediction History**: A sleek, glassmorphic history table showing recent predictions for quick reference.
- **Modern UI**: Clean, professional, and responsive glassmorphic design.
- **Vietnamese Localization**: Fully translated interface and scientific terminology for Vietnamese users.

## Tech Stack

### Frontend

- React 18
- TypeScript
- Vite
- Vanilla CSS (Glassmorphism design language)

### Backend

- FastAPI (Python)
- Uvicorn (ASGI server)

### Machine Learning

- `scikit-learn`: Random Forest classification model (`joblib` for serialization)
- `pymatgen` & `matminer`: Chemical formula parsing and featurization (Magpie descriptors)

## Directory Structure

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

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.9+
- pip (Python package installer)

### Installation

#### 1. Backend Setup

Open a terminal and navigate to the project root, then to the backend:

```bash
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install fastapi uvicorn scikit-learn pymatgen matminer joblib
```

#### 2. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend

# Install NPM packages
npm install
```

## Usage

To run the application locally, you will need to start both the backend and frontend servers.

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The backend API will run at `http://localhost:8000`.

### Start the Frontend Server

```bash
cd frontend
npm run dev
```

The frontend application will be available at the local URL provided by Vite (usually `http://localhost:5173`).

## Project Architecture & How it Works

1. **User Input**: The user enters a chemical formula (e.g., `NaCl`, `SiO2`) in the React frontend.
2. **API Request**: The frontend sends the formula to the FastAPI backend via a POST request.
3. **Featurization**: The backend uses `pymatgen` to parse the composition and `matminer` to extract Magpie descriptors (elemental properties based on the formula).
4. **Prediction**: The extracted features are passed into a pre-trained `scikit-learn` Random Forest model, which predicts whether the band gap is "High" or "Low".
5. **Response & Visualization**: The backend returns the prediction to the frontend, which displays it using a step-by-step loading animation, followed by the result and scientific explanation.

## License

Distributed under the MIT License. See `LICENSE` for more information.
