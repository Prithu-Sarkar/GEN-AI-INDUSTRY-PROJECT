# 🔐 Network Security — Phishing Detection ML Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue)
![DagsHub](https://img.shields.io/badge/DagsHub-Experiments-purple)

---

## 📌 Project Overview

This project builds an end-to-end Machine Learning pipeline to detect **phishing URLs** in network traffic. It covers the complete MLOps lifecycle — from raw data ingestion to model training — with two versions built for different deployment contexts.

---

## 🗂️ Two Versions of This Project

### Version 1 — `Networksecurity/` (Production Grade)
A fully production-ready implementation with:
- **FastAPI** REST endpoints (`/train`, `/predict`)
- **AWS S3** sync for artifact and model storage
- **Docker** containerization for deployment
- **CI/CD** pipeline via GitHub Actions
- Designed to run on cloud infrastructure (EC2, ECS, etc.)

### Version 2 — `NetworkSecurity_Phising/` (Colab MLOps Edition)
A deployment-free, reproducible ML pipeline built to run entirely in **Google Colab**:
- No Docker, no AWS, no server required
- All artifacts saved locally and downloadable
- **MLflow + DagsHub** for experiment tracking
- **MongoDB Atlas** as cloud data store
- Designed for learning, experimentation, and portfolio demonstration

---

## 🏗️ Project Structure (Version 2 — Colab Edition)

```
NetworkSecurity_Phising/
│
├── networksecurity/                    ← Core ML package
│   ├── components/
│   │   ├── data_ingestion.py          ← Pulls data from MongoDB Atlas
│   │   ├── data_validation.py         ← Schema check + drift detection
│   │   ├── data_transformation.py     ← KNN Imputer preprocessing
│   │   └── model_trainer.py           ← GridSearchCV + best model selection
│   │
│   ├── constant/
│   │   └── training_pipeline.py       ← All pipeline constants & configs
│   │
│   ├── entity/
│   │   ├── artifact_entity.py         ← Dataclasses for pipeline artifacts
│   │   └── config_entity.py           ← Config classes for each component
│   │
│   ├── exception/
│   │   └── exception.py               ← Custom exception with file & line info
│   │
│   ├── logging/
│   │   └── logger.py                  ← Timestamped file logging
│   │
│   ├── pipeline/
│   │   └── training_pipeline.py       ← Orchestrates all pipeline stages
│   │
│   └── utils/
│       ├── main_utils/utils.py        ← YAML, pickle, numpy helpers
│       └── ml_utils/
│           ├── model/estimator.py     ← NetworkModel wrapper class
│           └── metric/classification_metric.py  ← F1, Precision, Recall
│
├── data_schema/
│   └── schema.yaml                    ← 31-column schema definition
│
├── final_model/
│   ├── model.pkl                      ← Best trained model
│   └── preprocessor.pkl               ← Fitted KNN Imputer pipeline
│
├── Artifacts/                         ← Timestamped pipeline run outputs
│   └── <timestamp>/
│       ├── data_ingestion/
│       ├── data_validation/
│       ├── data_transformation/
│       └── model_trainer/
│
├── Network_Data/
│   └── phisingData.csv                ← Raw dataset (excluded from Git)
│
├── push_data.py                       ← One-time MongoDB data upload script
├── setup.py                           ← Package installation config
├── requirements.txt                   ← All dependencies
├── .gitignore                         ← Excludes secrets, models, data
└── NetworkSecurity_Phising_Detection.ipynb  ← Main Colab notebook
```

---

## ⚙️ Pipeline Stages

### 1. Data Ingestion
- Connects to **MongoDB Atlas** using `pymongo` + `certifi` (SSL)
- Pulls all records from the `KRISHAI.NetworkData` collection
- Saves raw data to feature store
- Splits into train/test (80/20) and saves as CSV

### 2. Data Validation
- Validates column count against `schema.yaml`
- Runs **Kolmogorov-Smirnov (KS) test** on every feature to detect dataset drift between train and test
- Saves a `report.yaml` with p-values and drift status per column

### 3. Data Transformation
- Drops target column (`Result`) and separates features
- Replaces `-1` labels with `0` (binary classification)
- Applies **KNN Imputer** (k=3, uniform weights) via `sklearn.Pipeline`
- Saves transformed numpy arrays + fitted preprocessor as `.pkl`

### 4. Model Training
- Trains 5 models: `RandomForest`, `DecisionTree`, `GradientBoosting`, `LogisticRegression`, `AdaBoost`
- Uses **GridSearchCV** (cv=3) for hyperparameter tuning on each
- Selects best model by R² score on test set
- Logs **F1, Precision, Recall** to **MLflow** (tracked on DagsHub)
- Saves best model + preprocessor wrapped in `NetworkModel` class

---

## 🛠️ Industry Practices Used

| Practice | Implementation |
|----------|---------------|
| **Modular Code** | Each pipeline stage is a separate class with single responsibility |
| **Custom Exception Handling** | `NetworkSecurityException` captures filename + line number |
| **Structured Logging** | Timestamped log files via Python `logging` module |
| **Config & Artifact Entities** | Dataclasses separate config from business logic |
| **Data Validation** | KS-test drift detection before transformation |
| **Experiment Tracking** | MLflow metrics logged to DagsHub remote server |
| **Preprocessing Pipeline** | `sklearn.Pipeline` ensures no data leakage |
| **Reproducibility** | Timestamped artifact directories per run |
| **Secret Management** | Credentials stored in Colab Secrets, never hardcoded |
| **Package Structure** | Installable Python package via `setup.py` |

---

## 📊 Dataset

- **Source:** UCI Phishing Websites Dataset
- **Features:** 30 binary/integer features (URL structure, domain info, HTML/JS behaviour)
- **Target:** `Result` → `1` (legitimate) / `0` (phishing, converted from `-1`)
- **Storage:** MongoDB Atlas (free M0 cluster)

---

## 🧰 Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.10 |
| ML | scikit-learn, KNNImputer, GridSearchCV |
| Data | MongoDB Atlas, pymongo, pandas, numpy |
| Tracking | MLflow, DagsHub |
| Environment | Google Colab |
| Packaging | setuptools, pip |
| Version Control | Git, GitHub |

---

## 🚀 How to Run (Colab)

1. Open `NetworkSecurity_Phising_Detection.ipynb` in Google Colab
2. Add secrets → `MONGO_DB_URL`, `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD`
3. Run all cells top to bottom
4. View experiment results at [DagsHub MLflow UI](https://dagshub.com/prithusarkar90/networksecurity/experiments)

---

## 📈 Results

| Metric | Value |
|--------|-------|
| Best Model | Random Forest / Gradient Boosting |
| Drift Detected | None (0/31 columns) |
| MLflow Tracked | ✅ F1, Precision, Recall per run |
