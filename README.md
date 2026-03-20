# ⛈️ Thunderstorm Forecasting System

> An end-to-end machine learning pipeline for predicting thunderstorm occurrence using atmospheric indices — with experiment tracking via MLflow / DagsHub, a real-time prediction interface via Streamlit, and a REST inference API via FastAPI.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://thunderstrom-forecast.streamlit.app/)
[![MLflow](https://img.shields.io/badge/Experiment%20Tracking-MLflow%20%2F%20DagsHub-0194E2?style=flat-square&logo=mlflow)](https://mlflow.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📑 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [Pipeline Phases](#pipeline-phases)
  - [Phase 1 — Data Engineering](#phase-1--data-engineering)
  - [Phase 2 — Model Training & Experiment Tracking](#phase-2--model-training--experiment-tracking)
  - [Phase 3 — Deployment & Serving](#phase-3--deployment--serving)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Reference](#api-reference)
- [Results](#results)
- [References](#references)

---

## Overview

Thunderstorm occurrence is a high-impact, low-frequency weather event. This project builds a binary classifier that predicts whether a thunderstorm (`TH = 1`) will occur on a given day, based on 12 atmospheric indices derived from radiosonde observations.

The pipeline covers the full ML lifecycle: raw data ingestion → preprocessing & merging → class imbalance handling (SMOTE) → multi-model training with MLflow tracking → best-model selection → Streamlit web app deployment → FastAPI inference endpoint.

---

## Project Structure

```
thunderstorm-forecasting/
│
├── data/
│   ├── raw/
│   │   ├── indices data.csv              # Atmospheric indices (SWEAT, K, CAPE, etc.) — 22,449 rows
│   │   └── surface_data.csv             # Surface observations with TH target — 14,397 rows
│   └── processed/
│       └── merged_df_all12k_combined.csv # Merged daily dataset — 11,873 rows, ready for modelling
│
├── models/
│   ├── best_model_Random_Forest.pkl     # Primary inference model
│   ├── KNN_best_model.pkl               # KNN alternative
│   └── scaler.pkl                       # Fitted StandardScaler
│
├── streamlit_app/
│   └── ui.py                            # Streamlit prediction interface
│
├── api/
│   └── main.py                          # FastAPI REST inference endpoint
│
├── experiments/
│   ├── experiment.ipynb                 # Exploratory notebook
│   └── mlruns/                          # Local MLflow run artefacts
│
├── outputs/
│   ├── feature_boxplots.png
│   ├── correlation_heatmap.png
│   ├── class_distribution.png
│   ├── cm_Random_Forest.png
│   ├── cm_KNN.png
│   └── model_comparison.csv
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Dataset

| Property | Details |
|----------|---------|
| **Source** | Radiosonde upper-air soundings + surface synoptic observations |
| **Raw files** | `indices data.csv` (22,449 rows × 18 cols), `surface_data.csv` (14,397 rows × 40 cols) |
| **Processed file** | `merged_df_all12k_combined.csv` (11,873 rows × 19 cols) |
| **Target** | `TH` — binary (0 = no thunderstorm, 1 = thunderstorm) |
| **Class ratio** | ~99.9% negative, ~0.1% positive (highly imbalanced) |
| **Period** | 1981–1992 (12 years of daily observations) |

### Feature Columns

| Feature | Description |
|---------|-------------|
| `SWEAT index` | Severe Weather Threat index |
| `Showalter index` | Lifted parcel instability index |
| `LIFTED index` | Surface-based lifted index |
| `K index` | Thunderstorm potential index |
| `Cross totals index` | Dewpoint vs 500hPa temp |
| `Vertical totals index` | 850hPa vs 500hPa temp difference |
| `Totals totals index` | Sum of cross + vertical totals |
| `TLCL` | Temperature at LCL (K) |
| `PLCL` | Pressure at LCL (hPa) |
| `CINE` | Convective Inhibition Energy (J/kg) |
| `CAPE` | Convective Available Potential Energy (J/kg) |
| `PRECIPITABLE WATER` | Total column precipitable water |

---

## Pipeline Phases

### Phase 1 — Data Engineering

**Goal:** Transform two separate raw CSV files into a single clean daily dataset ready for modelling.

**Steps:**

1. **Load raw data** — `indices data.csv` carries upper-air sounding indices at 00 UTC and 12 UTC per day; `surface_data.csv` carries daily surface observations including the `TH` (thunderstorm) target flag.

2. **Column normalisation** — The indices file uses the row index as the year (1981–1992) and column headers as month, day, and GMT hour. These are renamed to a consistent `Year / Month / Day / Hour` scheme.

3. **Daily aggregation** — The two daily radiosonde readings (00 and 12 UTC) are averaged to produce a single representative index value per day using `groupby(['Year','Month','Day']).mean()`.

4. **Target cleaning** — The `TH` column in the surface file contains mixed types (`'0'`, `'1'`, `' '`). These are coerced to numeric with `pd.to_numeric(..., errors='coerce')`, NaNs filled with 0, and cast to `int`.

5. **Inner merge** — Both daily frames are joined on `Year`, `Month`, `Day` keys, yielding 11,873 matched daily records.

6. **Persist processed data** — The merged frame is saved to `data/processed/merged_df_all12k_combined.csv` for all downstream steps.

**Key files:** `data/raw/indices data.csv`, `data/raw/surface_data.csv` → `data/processed/merged_df_all12k_combined.csv`

---

### Phase 2 — Model Training & Experiment Tracking

**Goal:** Train multiple classifiers, handle class imbalance with SMOTE, evaluate on held-out data, and log every run to MLflow / DagsHub.

**Steps:**

1. **Feature selection** — 12 atmospheric indices are used as input features (see table above). Rows with any NaN in these columns are dropped before splitting.

2. **Train / test split** — 80 / 20 stratified split (`random_state=42`) to preserve the minority class ratio in both sets.

3. **SMOTE oversampling** — Applied exclusively to the training set. Synthetic Minority Over-sampling Technique generates new minority-class samples to balance the training distribution, preventing the model from simply predicting the majority class. The test set is never touched by SMOTE.

4. **Standard scaling** — `StandardScaler` is fit on the SMOTE-resampled training data and applied to both train and test sets. The fitted scaler is serialised to `models/scaler.pkl`.

5. **Multi-model training** — Four classifiers are trained and evaluated:

   | Model | Key Hyperparameters |
   |-------|-------------------|
   | Random Forest | `n_estimators=200`, `max_depth=10`, `class_weight='balanced'` |
   | K-Nearest Neighbours | `n_neighbors=5`, `weights='distance'` |
   | Logistic Regression | `max_iter=500`, `class_weight='balanced'` |
   | Decision Tree | `max_depth=8`, `class_weight='balanced'` |

6. **MLflow logging** — Each model is trained inside a `mlflow.start_run()` context. The following are logged per run:
   - **Parameters:** all model hyperparameters, SMOTE flag, scaler type, train/test sizes, feature list
   - **Metrics:** accuracy, precision, recall, F1-score, ROC-AUC
   - **Artefacts:** confusion matrix PNG, serialised model via `mlflow.sklearn.log_model()`

7. **Best model selection** — The model with the highest F1-score on the test set is selected (F1 is preferred over accuracy given the severe class imbalance). Both the Random Forest and KNN models are additionally persisted individually since both are used in the Streamlit UI.

**MLflow tracking URI:** configured via `MLFLOW_TRACKING_URI` environment variable — either DagsHub remote or a local `file://` path.

**Key files:** `models/best_model_Random_Forest.pkl`, `models/KNN_best_model.pkl`, `models/scaler.pkl`, `outputs/model_comparison.csv`

---

### Phase 3 — Deployment & Serving

**Goal:** Expose the trained model as both a browser-accessible Streamlit web application and a programmatic FastAPI REST endpoint, tunnelled publicly via ngrok.

#### Streamlit Application (`streamlit_app/ui.py`)

- Loads `best_model_Random_Forest.pkl` and `scaler.pkl` via `@st.cache_resource` (loaded once, reused across sessions).
- Sidebar contains 12 numeric inputs — one per atmospheric index — pre-populated with climatological default values.
- On clicking **Predict**, inputs are assembled into a DataFrame, scaled, and passed to the model. The prediction (THUNDERSTORM / NO THUNDERSTORM), class probabilities, and a summary table are displayed.
- Served on port `8501` and tunnelled via ngrok using `pyngrok`.

#### FastAPI Inference API (`api/main.py`)

- `POST /predict` — accepts a JSON body with 12 float fields (snake_case index names), returns `prediction` (int), `label` (string), and `probability_thunderstorm` (float).
- `GET /` — health check / API description.
- Model and scaler are loaded at startup for low-latency inference.

#### Serving via ngrok

```python
from pyngrok import ngrok
ngrok.set_auth_token(NGROK_AUTHTOKEN)
public_url = ngrok.connect(8501)   # Streamlit
```

A public HTTPS URL is printed to the console and can be shared immediately.

**Key files:** `streamlit_app/ui.py`, `api/main.py`

---

## Installation

```bash
git clone https://github.com/d-hackmt/thunderstrom-forecast.git
cd thunderstrom-forecast

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**`requirements.txt`**
```
pandas
numpy
scikit-learn
imbalanced-learn
mlflow
dagshub
streamlit
pyngrok
joblib
fastapi
uvicorn
matplotlib
seaborn
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MLFLOW_TRACKING_URI` | Yes | DagsHub MLflow endpoint or `file://...` for local |
| `MLFLOW_TRACKING_USERNAME` | DagsHub only | DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | DagsHub only | DagsHub access token |
| `MONGO_DB_URL` | Optional | MongoDB connection string for raw data ingestion |
| `NGROK_AUTHTOKEN` | Serving only | ngrok authentication token |

Set these in a `.env` file or export directly in your shell. When running inside a notebook environment, load them from the secrets manager provided by the platform.

---

## Running the Project

### 1. Training Pipeline

```bash
# Set env vars first, then run the notebook or script
python experiments/train.py   # if using a standalone script
# OR open experiments/experiment.ipynb and run all cells
```

### 2. Streamlit App (local)

```bash
streamlit run streamlit_app/ui.py
# Open http://localhost:8501
```

### 3. FastAPI Server (local)

```bash
uvicorn api.main:app --reload --port 8000
# Docs at http://localhost:8000/docs
```

---

## API Reference

### `POST /predict`

**Request body:**
```json
{
  "sweat_index": 80.0,
  "showalter_index": 5.0,
  "lifted_index": 0.0,
  "k_index": 20.0,
  "cross_totals": 20.0,
  "vertical_totals": 25.0,
  "totals_totals": 45.0,
  "tlcl": 280.0,
  "plcl": 900.0,
  "cine": -10.0,
  "cape": 100.0,
  "precipitable_water": 30.0
}
```

**Response:**
```json
{
  "prediction": 0,
  "label": "NO THUNDERSTORM",
  "probability_thunderstorm": 0.032
}
```

---

## Results

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Random Forest | — | — | — | — | — |
| KNN | — | — | — | — | — |
| Logistic Regression | — | — | — | — | — |
| Decision Tree | — | — | — | — | — |

> Populate this table from `outputs/model_comparison.csv` after running the training pipeline.

---

## References

| Resource | Link |
|----------|------|
| Live Demo | https://thunderstrom-forecast.streamlit.app/ |
| GitHub Repository | https://github.com/d-hackmt/thunderstrom-forecast |
| MLflow Documentation | https://mlflow.org/ |
| Streamlit Cloud | https://streamlit.io/cloud |
| DagsHub | https://dagshub.com/ |
| FastAPI | https://fastapi.tiangolo.com/ |
| scikit-learn | https://scikit-learn.org/ |
| imbalanced-learn (SMOTE) | https://imbalanced-learn.org/ |
