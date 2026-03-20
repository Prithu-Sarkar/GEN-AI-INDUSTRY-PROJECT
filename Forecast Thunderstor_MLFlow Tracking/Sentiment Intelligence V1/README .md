# Social Video Audience Sentiment Intelligence

> **End-to-end NLP system for real-time YouTube comment sentiment analysis** — from raw data ingestion through reproducible ML pipelines, experiment tracking, model registry, REST API serving, and a Chrome Extension that surfaces predictions directly on YouTube.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [ML Pipeline](#ml-pipeline)
- [Deployment Variants](#deployment-variants)
  - [Variant A — Cloud Infrastructure (AWS)](#variant-a--cloud-infrastructure-aws)
  - [Variant B — Notebook-based Execution](#variant-b--notebook-based-execution)
- [API Reference](#api-reference)
- [Chrome Extension](#chrome-extension)
- [Experiment Tracking](#experiment-tracking)
- [Configuration](#configuration)
- [Assignments & Exercises](#assignments--exercises)

---

## Overview

This system ingests YouTube / Reddit comment data, trains a **LightGBM** multi-class classifier on top of **TF-IDF** features, and exposes the trained model via a **Flask REST API**. A **Chrome Extension** queries that API live on YouTube video pages, displaying per-comment sentiment alongside aggregated charts and word clouds.

The entire ML lifecycle is orchestrated with **DVC** (Data Version Control), and every experiment run — metrics, artifacts, confusion matrices — is logged to **MLflow** tracked via **DagsHub**.

**Sentiment labels**

| Label | Class | Description |
|-------|-------|-------------|
| `1`   | Positive | Enthusiastic / appreciative comments |
| `0`   | Neutral  | Informational / indifferent comments |
| `-1`  | Negative | Critical / dissatisfied comments |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Chrome Extension                         │
│               (yt-chrome-plugin-frontend)                    │
└─────────────────────────┬────────────────────────────────────┘
                          │  HTTP POST
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    Flask REST API                            │
│                   (flask_api/main.py)                        │
│                                                              │
│  /predict   /predict_with_timestamps   /generate_chart       │
│  /generate_wordcloud   /generate_trend_graph                 │
└──────┬─────────────────┬───────────────────────────────────┘
       │                 │
       ▼                 ▼
┌────────────┐   ┌──────────────────┐
│ lgbm_      │   │ tfidf_           │
│ model.pkl  │   │ vectorizer.pkl   │
└────────────┘   └──────────────────┘
       ▲                 ▲
       └────────┬────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│                    DVC Pipeline (dvc.yaml)                   │
│                                                              │
│  data_ingestion → data_preprocessing → model_building        │
│       → model_evaluation → model_registration               │
└───────────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│              MLflow Experiment Tracking (DagsHub)            │
│         Metrics · Artifacts · Model Registry · Tags         │
└──────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **ML Model** | LightGBM (`LGBMClassifier`) |
| **Feature Engineering** | Scikit-learn `TfidfVectorizer` |
| **NLP Pre-processing** | NLTK — stopword removal, WordNet lemmatization |
| **Pipeline Orchestration** | DVC 3.x |
| **Experiment Tracking** | MLflow 2.x + DagsHub |
| **Backend API** | Flask 3.x + Flask-CORS |
| **Visualisation** | Matplotlib, Seaborn, WordCloud |
| **Data Layer** | MongoDB (remote), Pandas, NumPy |
| **Frontend** | Chrome Extension — Manifest V3 (HTML / CSS / JS) |
| **Containerisation** | Docker |
| **Cloud** | AWS EC2, AWS ECR, AWS IAM |
| **CI/CD** | GitHub Actions (self-hosted runner on EC2) |
| **Version Control** | Git + DVC |

---

## Project Structure

```
Social-Video-Audience-Sentiment-Intelligence/
│
├── src/
│   ├── data/
│   │   ├── data_ingestion.py       # Stage 1 — fetch, clean, train/test split
│   │   └── data_preprocessing.py  # Stage 2 — NLP normalisation pipeline
│   └── model/
│       ├── model_building.py       # Stage 3 — TF-IDF + LightGBM training
│       ├── model_evaluation.py     # Stage 4 — metrics, MLflow logging
│       └── register_model.py       # Stage 5 — MLflow Model Registry
│
├── flask_api/
│   └── main.py                     # REST API — prediction + visualisation endpoints
│
├── yt-chrome-plugin-frontend/
│   ├── manifest.json               # Chrome Extension Manifest V3
│   ├── popup.html
│   ├── popup.js
│   └── style.css
│
├── data/
│   ├── raw/                        # train.csv, test.csv  (DVC-tracked)
│   └── interim/                    # train_processed.csv, test_processed.csv
│
├── notebooks/                      # Exploratory notebooks (6 experiments)
│
├── dvc.yaml                        # Pipeline DAG definition
├── params.yaml                     # Centralised hyperparameter config
├── requirements.txt
├── setup.py
└── README.md
```

---

## ML Pipeline

The pipeline is fully reproducible via `dvc repro`. Each stage declares its inputs, outputs, and parameters — DVC re-runs only the stages affected by a change.

```
data_ingestion
      │
      ▼
data_preprocessing
      │
      ▼
model_building
      │
      ▼
model_evaluation   ──►  MLflow run (metrics + artifacts)
      │
      ▼
model_registration ──►  MLflow Model Registry (Staging)
```

### Stage Details

#### Stage 1 — Data Ingestion (`src/data/data_ingestion.py`)
- Downloads the Reddit comments dataset from a public URL
- Drops nulls, duplicates, and empty strings
- Performs stratified train / test split (`test_size` from `params.yaml`)
- Outputs: `data/raw/train.csv`, `data/raw/test.csv`

#### Stage 2 — Data Preprocessing (`src/data/data_preprocessing.py`)
- Lowercases and strips whitespace
- Removes non-alphanumeric characters
- Removes stopwords — retains negation tokens (`not`, `no`, `but`, `however`, `yet`) for sentiment fidelity
- Applies WordNet lemmatization
- Outputs: `data/interim/train_processed.csv`, `data/interim/test_processed.csv`

#### Stage 3 — Model Building (`src/model/model_building.py`)
- Fits `TfidfVectorizer` on the training corpus (configurable `max_features`, `ngram_range`)
- Trains `LGBMClassifier` with L1/L2 regularisation and balanced class weights
- Persists: `lgbm_model.pkl`, `tfidf_vectorizer.pkl`

#### Stage 4 — Model Evaluation (`src/model/model_evaluation.py`)
- Transforms test set using the fitted vectorizer
- Computes per-class precision, recall, F1-score
- Logs all metrics, artifacts, confusion matrix, and model signature to MLflow
- Writes `experiment_info.json` for the registration stage

#### Stage 5 — Model Registration (`src/model/register_model.py`)
- Reads `experiment_info.json`
- Registers the model version in the MLflow Model Registry
- Transitions to **Staging** stage

---

## Deployment Variants

### Variant A — Cloud Infrastructure (AWS)

Production-grade deployment with Docker, AWS ECR, EC2, and a CI/CD pipeline via GitHub Actions.

#### Prerequisites
- AWS account with IAM user credentials (ECR push + EC2 access)
- Docker installed locally
- GitHub repository with Actions enabled

#### 1. Clone and configure

```bash
git clone https://github.com/<your-org>/Social-Video-Audience-Sentiment-Intelligence.git
cd Social-Video-Audience-Sentiment-Intelligence
```

#### 2. Create and activate environment

```bash
conda create -n sentiment python=3.11 -y
conda activate sentiment
pip install -r requirements.txt
```

#### 3. Configure AWS credentials

```bash
aws configure
# AWS Access Key ID:     <your-key>
# AWS Secret Access Key: <your-secret>
# Default region:        us-east-1
# Output format:         json
```

#### 4. Run the DVC pipeline

```bash
dvc init
dvc repro        # executes all 5 stages
dvc dag          # visualise the dependency graph
```

#### 5. Set GitHub Actions secrets

In your repository → **Settings → Secrets and Variables → Actions**, add:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret |
| `AWS_REGION` | e.g. `us-east-1` |
| `AWS_ECR_LOGIN_URI` | ECR registry URI |
| `ECR_REPOSITORY_NAME` | Name of your ECR repository |
| `MLFLOW_TRACKING_URI` | DagsHub / MLflow server URL |
| `MLFLOW_TRACKING_USERNAME` | DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | DagsHub token |

#### 6. CI/CD workflow

On every push to `main`, GitHub Actions will:

1. Build the Docker image
2. Push it to AWS ECR
3. SSH into the EC2 instance (self-hosted runner)
4. Pull the latest image from ECR
5. Stop the existing container and start the updated one

#### 7. Flask API — local test

```bash
cd flask_api
python main.py
```

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"comments": ["This video is awesome!", "Very poor explanation."]}'
```

---

### Variant B — Notebook-based Execution

Full pipeline execution within a managed notebook environment — no cloud infrastructure required. Uses `google.colab.userdata` for secret management.

#### Prerequisites
- Jupyter-compatible notebook environment
- Secrets configured (see below)

#### 1. Configure secrets

Add the following secrets to your environment's secret store:

| Secret | Value |
|--------|-------|
| `MONGO_DB_URL` | MongoDB connection string |
| `MLFLOW_TRACKING_URI` | DagsHub tracking URI |
| `MLFLOW_TRACKING_USERNAME` | DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | DagsHub token |

#### 2. Execute the notebook

Open `Sentiment_Intelligence_Colab.ipynb` and run cells sequentially:

| Cell block | Action |
|---|---|
| **Install dependencies** | Installs all packages from `requirements.txt` |
| **Set environment variables** | Loads secrets, configures MLflow tracking URI |
| **Scaffold project** | Creates directory tree and `__init__.py` files |
| **Write config files** | Writes `params.yaml` and `dvc.yaml` |
| **Write source modules** | Writes all 5 pipeline `.py` files to disk |
| **Run Stage 1** | Executes `data_ingestion.py` — downloads and splits data |
| **Run Stage 2** | Executes `data_preprocessing.py` — NLP normalisation |
| **Run Stage 3** | Executes `model_building.py` — TF-IDF + LightGBM |
| **Run Stage 4** | Executes `model_evaluation.py` — metrics + MLflow logging |
| **Run Stage 5** | Executes `register_model.py` — Model Registry |
| **Flask API test** | Spins up the API, runs test predictions, shuts down |
| **Download artifacts** | Zips and downloads the `src/` directory |

#### 3. Download trained artifacts

```python
import zipfile, os
from google.colab import files

EXCLUDE = {'mlruns', '__pycache__', '.git', '.ipynb_checkpoints'}

with zipfile.ZipFile('src_artifacts.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, filenames in os.walk('src'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for filename in filenames:
            zf.write(os.path.join(root, filename))

files.download('src_artifacts.zip')
```

#### 4. Toggle MLflow backend

```python
USE_DAGSHUB = True   # False → logs to local ./mlruns directory
```

---

## API Reference

All endpoints accept and return `application/json` unless otherwise noted.

Base URL (local): `http://localhost:5000`

---

### `POST /predict`

Classify a batch of comments.

**Request**
```json
{
  "comments": ["This video is awesome!", "Very poor explanation."]
}
```

**Response**
```json
[
  { "comment": "This video is awesome!", "sentiment": 1 },
  { "comment": "Very poor explanation.", "sentiment": -1 }
]
```

---

### `POST /predict_with_timestamps`

Classify comments with associated timestamps for trend analysis.

**Request**
```json
{
  "comments": [
    { "text": "Great content!", "timestamp": "2024-01-15T10:30:00" },
    { "text": "Not helpful at all.", "timestamp": "2024-02-03T08:15:00" }
  ]
}
```

**Response**
```json
[
  { "comment": "Great content!", "sentiment": "1", "timestamp": "2024-01-15T10:30:00" },
  { "comment": "Not helpful at all.", "sentiment": "-1", "timestamp": "2024-02-03T08:15:00" }
]
```

---

### `POST /generate_chart`

Returns a PNG pie chart of sentiment distribution.

**Request**
```json
{ "sentiment_counts": { "1": 120, "0": 45, "-1": 35 } }
```

**Response** — `image/png`

---

### `POST /generate_wordcloud`

Returns a PNG word cloud generated from the provided comments.

**Request**
```json
{ "comments": ["awesome video", "great explanation", "very helpful"] }
```

**Response** — `image/png`

---

### `POST /generate_trend_graph`

Returns a PNG line chart showing monthly sentiment percentages over time.

**Request**
```json
{
  "sentiment_data": [
    { "sentiment": 1,  "timestamp": "2024-01-10T00:00:00" },
    { "sentiment": -1, "timestamp": "2024-02-14T00:00:00" }
  ]
}
```

**Response** — `image/png`

---

## Chrome Extension

The extension integrates directly with YouTube video pages.

### Setup

1. Navigate to `chrome://extensions` in Chrome
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked** and select the `yt-chrome-plugin-frontend/` directory
4. The extension icon will appear in the Chrome toolbar

### How it works

1. User opens a YouTube video page
2. Clicks the extension icon → popup renders
3. Extension scrapes visible comments from the DOM
4. Sends a `POST /predict_with_timestamps` request to the Flask API
5. Displays per-comment sentiment labels, a pie chart, word cloud, and trend graph

### Getting a YouTube Data API Key

Required if using the YouTube Data API v3 for comment fetching:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → **APIs & Services → Enable APIs**
3. Enable **YouTube Data API v3**
4. Create credentials → **API Key**
5. Set the key in the extension's `popup.js`

Reference: [YouTube API key setup guide](https://www.youtube.com/watch?v=i_FdiQMwKiw)

---

## Experiment Tracking

All training runs are logged to **MLflow** via **DagsHub**.

### Tracked per run

| Category | Items |
|---|---|
| **Parameters** | `test_size`, `ngram_range`, `max_features`, `learning_rate`, `max_depth`, `n_estimators` |
| **Metrics** | Per-class precision, recall, F1-score for Negative / Neutral / Positive |
| **Artifacts** | `lgbm_model`, `tfidf_vectorizer.pkl`, `confusion_matrix_Test_Data.png` |
| **Tags** | `model_type: LightGBM`, `task: Sentiment Analysis`, `dataset: YouTube Comments` |

### Model Registry stages

```
None → Staging → Production → Archived
```

After evaluation, models are automatically registered and transitioned to **Staging**. Manual promotion to **Production** is performed via the MLflow UI after review.

---

## Configuration

All pipeline hyperparameters are centralised in `params.yaml`:

```yaml
data_ingestion:
  test_size: 0.20          # fraction held out for evaluation

model_building:
  ngram_range: [1, 3]      # TF-IDF n-gram range (unigrams → trigrams)
  max_features: 1000       # maximum vocabulary size
  learning_rate: 0.09      # LightGBM learning rate
  max_depth: 20            # maximum tree depth
  n_estimators: 367        # number of boosting rounds
```

Modify this file and re-run `dvc repro` — DVC will detect the parameter change and re-execute only the affected downstream stages.

---

## Assignments & Exercises

### Quiz — Architecture & Concepts

1. What is the primary purpose of `dvc.yaml` in this project?
2. Which command reproduces the entire pipeline from scratch?
3. How does the Chrome Extension communicate with the ML model?
4. What technique converts text to numerical features?
5. Why must `tfidf_vectorizer.pkl` be saved alongside `lgbm_model.pkl`?

### Practical Assignments

#### Assignment 1 — Model Improvement
- Swap `TfidfVectorizer` for `CountVectorizer` and benchmark the delta in F1-score
- Replace LightGBM with `RandomForestClassifier` — add its hyperparameters to `params.yaml`
- Analyse class imbalance in `data/raw` and experiment with oversampling (SMOTE)

#### Assignment 2 — API Extension
- Extend `/predict` to return prediction probability / confidence alongside the label
- Add a request logging middleware that appends every request to `api_logs.csv`
- Implement a `/health` endpoint that returns model metadata (version, training date)

#### Assignment 3 — Frontend Enhancement
- Add a loading spinner to the extension popup during API calls
- Implement graceful error handling when the API is unreachable
- Display confidence scores next to each sentiment label if Assignment 2 is completed

---

## License

This project is intended for educational and research purposes.
