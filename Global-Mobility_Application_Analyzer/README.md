# Global Mobility Application Analyzer

**Predicting US Visa Certification outcomes using an end-to-end machine learning pipeline.**

The project is available in three execution environments. Each shares an identical ML core — data ingestion, validation, transformation, model training, and prediction — while the infrastructure layer (data source, experiment tracking, deployment) is adapted to the target environment.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [ML Pipeline Architecture](#ml-pipeline-architecture)
- [Version Comparison](#version-comparison)
- [Version 1 — Production (MongoDB + AWS + Docker)](#version-1--production-mongodb--aws--docker)
- [Version 2 — Google Colab (Local + MLflow/DagsHub)](#version-2--google-colab-local--mlflowdagshub)
- [Version 3 — Local Development (Fully Offline)](#version-3--local-development-fully-offline)
- [Project Structure](#project-structure)
- [Model Details](#model-details)
- [Results](#results)
- [License](#license)

---

## Problem Statement

The US Office of Foreign Labor Certification (OFLC) processes hundreds of thousands of visa applications annually. This project builds a binary classifier that predicts whether a visa application will be **Certified** or **Denied**, based on applicant and employer attributes submitted at the time of filing.

**Target column:** `case_status` — `Certified` (0) or `Denied` (1)

---

## Dataset

| Property | Detail |
|---|---|
| Source | US Department of Labor — OFLC Performance Data |
| File | `Visadataset.csv` / `visa.csv` |
| Rows | ~25,480 |
| Features | 11 input features + 1 target |
| Class imbalance | Addressed via SMOTEENN resampling |

**Input Features**

| Feature | Type | Description |
|---|---|---|
| `continent` | Categorical | Continent of the employee's country of origin |
| `education_of_employee` | Categorical | Highest education level attained |
| `has_job_experience` | Binary (Y/N) | Whether the applicant has prior job experience |
| `requires_job_training` | Binary (Y/N) | Whether the role requires job training |
| `no_of_employees` | Numeric | Number of employees at the sponsoring company |
| `yr_of_estab` | Numeric | Year the sponsoring company was established |
| `region_of_employment` | Categorical | US region where the job is located |
| `prevailing_wage` | Numeric | Wage offered for the position |
| `unit_of_wage` | Categorical | Wage unit — Hour, Week, Month, or Year |
| `full_time_position` | Binary (Y/N) | Whether the role is full-time |
| `company_age` | Engineered | Derived as `CURRENT_YEAR - yr_of_estab` |

---

## ML Pipeline Architecture

All three versions share the same five-stage pipeline. The stages execute sequentially and each produces a typed artifact that is passed to the next stage.

```
Raw CSV / MongoDB
      |
      v
+------------------+
|  Data Ingestion  |  Read source → feature store → train/test split (80/20)
+------------------+
      |
      v
+--------------------+
|  Data Validation   |  Schema check → column existence → drift detection
+--------------------+
      |
      v
+------------------------+
|  Data Transformation   |  company_age engineering → encoding → scaling → SMOTEENN
+------------------------+
      |
      v
+------------------+
|  Model Trainer   |  GridSearchCV → best model → VisaModel(preprocessor + classifier)
+------------------+
      |
      v
+---------------------+
|  Model Evaluation   |  Compare new model vs production model (V1 only)
+---------------------+
      |
      v
+---------------+
|  Model Pusher |  Upload best model to S3 (V1 only)
+---------------+
```

**Transformation details**

| Step | Columns Affected | Method |
|---|---|---|
| One-Hot Encoding | `continent`, `unit_of_wage`, `region_of_employment` | `sklearn.OneHotEncoder` |
| Ordinal Encoding | `has_job_experience`, `requires_job_training`, `full_time_position`, `education_of_employee` | `sklearn.OrdinalEncoder` |
| Power Transform | `no_of_employees`, `company_age` | `PowerTransformer(method='yeo-johnson')` |
| Standard Scaling | `no_of_employees`, `prevailing_wage`, `company_age` | `sklearn.StandardScaler` |
| Resampling | All features | `imblearn.SMOTEENN(sampling_strategy='minority')` |

---

## Version Comparison

| Capability | V1 — Production | V2 — Colab | V3 — Local Dev |
|---|:---:|:---:|:---:|
| Data source | MongoDB Atlas | Local CSV upload | Local CSV |
| Drift detection | Evidently AI | SciPy KS-test | SciPy KS-test |
| Model selection | neuro_mf | Custom ModelFactory | Custom ModelFactory |
| Experiment tracking | — | MLflow + DagsHub | MLflow (local) |
| Model storage | AWS S3 | Local filesystem | Local filesystem |
| Model evaluation | vs. S3 production model | Local only | Local only |
| Deployment | Docker + EC2 via GitHub Actions | — | — |
| Prediction interface | FastAPI web app | Notebook cell | Python script |
| Secrets management | GitHub Actions secrets | Colab Secrets | `.env` file |

---

## Version 1 — Production (MongoDB + AWS + Docker)

The full production stack. Data is sourced from MongoDB Atlas, the best model is evaluated against the version currently in S3, and the winner is deployed automatically via GitHub Actions CI/CD to an EC2 instance running behind a FastAPI server.

### Prerequisites

- Python 3.8
- MongoDB Atlas cluster with the visa collection loaded
- AWS account with S3 and ECR access
- Docker

### Installation

```bash
git clone https://github.com/entbappy/Global-Mobility-Application-Analyzer.git
cd Global-Mobility-Application-Analyzer

conda create -n visa python=3.8 -y
conda activate visa

pip install -r requirements.txt
```

### Environment Variables

```bash
export MONGODB_URL="mongodb+srv://<user>:<password>@cluster.mongodb.net"
export AWS_ACCESS_KEY_ID=<your_key_id>
export AWS_SECRET_ACCESS_KEY=<your_secret_key>
```

### Run

```bash
# Start the FastAPI server (triggers training via /train endpoint)
python app.py

# Or run training directly
python demo.py
```

Access the app at `http://0.0.0.0:8080`.

### Pipeline Stages (V1 only)

**Model Evaluation** compares the newly trained model's F1 score against the model currently stored in `s3://myvisabuc2025/model.pkl`. The new model is accepted only if it improves F1 by more than the configured threshold (`MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE = 0.02`).

**Model Pusher** uploads the accepted model to S3 under the `model-registry` key path. The FastAPI prediction pipeline then fetches the model from S3 at inference time via `VisaEstimator`.

### CI/CD — AWS with GitHub Actions

The `.github/workflows/cicd.yaml` workflow automates the full deployment cycle on every push to `main`:

```
Push to main
    |
    v
Build Docker image
    |
    v
Push image to AWS ECR (315865595366.dkr.ecr.us-east-1.amazonaws.com/visarepo)
    |
    v
SSH into EC2 (self-hosted runner)
    |
    v
Pull image from ECR → docker run
```

**Required GitHub Secrets**

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `ECR_REPO` | ECR repository URI |
| `MONGODB_URL` | MongoDB Atlas connection string |

**Required IAM Policies**

- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEC2FullAccess`

---

## Version 2 — Google Colab (Local + MLflow/DagsHub)

Self-contained notebook version. No cloud infrastructure required. Drift detection uses SciPy's Kolmogorov-Smirnov test in place of Evidently (which is incompatible with NumPy 2.x shipped by Colab). Experiment tracking is handled by MLflow pointed at DagsHub or saved locally.

### File

```
Global_Mobility_Application_Analyzer.ipynb
```

### Setup

Open the notebook in Google Colab and add the following secrets via the key icon in the left sidebar:

| Secret Key | Description |
|---|---|
| `MONGO_DB_URL` | MongoDB URL (optional — Colab reads from local CSV) |
| `MLFLOW_TRACKING_URI` | DagsHub MLflow tracking URI |
| `MLFLOW_TRACKING_USERNAME` | DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | DagsHub access token |

### Notebook Cell Order

| Cell | Purpose |
|---|---|
| 1 | Install packages (`mlflow`, `dagshub`, `dill`, etc.) |
| 2 | Set environment variables from Colab Secrets |
| 3 | Upload `Visadataset.csv` |
| 4 | Create project directory structure |
| 5–6 | Write `config/schema.yaml` and `config/model.yaml` |
| 7–15 | Write all Python source modules to `/content/visa/` |
| 16–19 | Run pipeline stages 1–4 |
| 20 | Run sample predictions |
| 21 | Zip and download all artifacts |

### MLflow Tracking

Every training run logs the following to MLflow automatically:

```
US_Visa_Approval_Prediction/
  └── <run_name: model class>
        ├── params/          # Best GridSearchCV hyperparameters
        ├── metrics/         # f1_score, precision_score, recall_score
        ├── tags/            # model_name, best_cv_f1
        └── artifacts/
              ├── model/             # sklearn estimator (mlflow.sklearn)
              ├── visa_model_pkl/    # VisaModel wrapper (preprocessor + classifier)
              ├── preprocessing/     # preprocessing.pkl
              └── drift_report/      # report.yaml (KS-test results)
```

Set `USE_DAGSHUB = False` in the env cell to log runs locally to `/content/mlruns` instead.

### Drift Detection (KS-Test)

Drift is evaluated on all numerical columns (`no_of_employees`, `prevailing_wage`, `yr_of_estab`) using a two-sample KS test between the train and test splits. A column is flagged as drifted when its p-value falls below `0.05`. Overall dataset drift is reported as `True` when more than half of the numerical columns drift.

### Artifacts Saved

After running all cells, the final zip contains:

```
Global_Mobility_Analyzer_outputs.zip
  ├── artifact/
  │     └── <timestamp>/
  │           ├── data_ingestion/
  │           │     ├── feature_store/visa.csv
  │           │     └── ingested/train.csv, test.csv
  │           ├── data_validation/
  │           │     └── drift_report/report.yaml
  │           ├── data_transformation/
  │           │     ├── transformed/train.npy, test.npy
  │           │     └── transformed_object/preprocessing.pkl
  │           └── model_trainer/
  │                 └── trained_model/model.pkl
  ├── logs/
  │     └── <timestamp>.log
  ├── config/
  │     ├── schema.yaml
  │     └── model.yaml
  └── mlruns/                   # present if USE_DAGSHUB = False
        └── <experiment_id>/
```

---

## Version 3 — Local Development (Fully Offline)

Runs entirely on a local machine with no internet access required after the initial `pip install`. Uses the same code as V2 but executed as standalone Python scripts rather than a notebook.

### Installation

```bash
git clone https://github.com/entbappy/Global-Mobility-Application-Analyzer.git
cd Global-Mobility-Application-Analyzer

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Copy your dataset to the project root:

```bash
cp /path/to/Visadataset.csv ./Visadataset.csv
```

Set MLflow to track locally:

```bash
export MLFLOW_TRACKING_URI="file://$(pwd)/mlruns"
```

### Run the Full Pipeline

```python
# demo.py
import sys
sys.path.insert(0, ".")

from visa.pipeline.training_pipeline import TrainingPipeline

pipeline = TrainingPipeline()
model_artifact = pipeline.run_pipeline()

print(f"Model saved  : {model_artifact.trained_model_file_path}")
print(f"F1 Score     : {model_artifact.metric_artifact.f1_score:.4f}")
print(f"Precision    : {model_artifact.metric_artifact.precision_score:.4f}")
print(f"Recall       : {model_artifact.metric_artifact.recall_score:.4f}")
```

```bash
python demo.py
```

### Run a Single Prediction

```python
from visa.pipeline.prediction_pipeline import VisaData, VisaClassifier
from visa.entity.estimator import TargetValueMapping

classifier = VisaClassifier(model_path="artifact/<timestamp>/model_trainer/trained_model/model.pkl")

applicant = VisaData(
    continent="Asia",
    education_of_employee="Master's",
    has_job_experience="Y",
    requires_job_training="N",
    no_of_employees=5000,
    region_of_employment="Northeast",
    prevailing_wage=80000,
    unit_of_wage="Year",
    full_time_position="Y",
    company_age=20,
)

df = applicant.get_usvisa_input_data_frame()
prediction = classifier.predict(df)[0]
label = TargetValueMapping().reverse_mapping()[int(prediction)]
print(f"Prediction: {label}")
```

### View MLflow UI Locally

```bash
mlflow ui --backend-store-uri ./mlruns
# Open http://127.0.0.1:5000
```

---

## Project Structure

```
Global-Mobility-Application-Analyzer/
├── visa/
│   ├── components/
│   │   ├── data_ingestion.py        # Stage 1: load + split
│   │   ├── data_validation.py       # Stage 2: schema + drift check
│   │   ├── data_transformation.py   # Stage 3: encode + scale + resample
│   │   ├── model_trainer.py         # Stage 4: GridSearchCV + MLflow logging
│   │   ├── model_evaluation.py      # Stage 5: compare vs production (V1)
│   │   └── model_pusher.py          # Stage 6: upload to S3 (V1)
│   ├── pipeline/
│   │   ├── training_pipeline.py     # Orchestrates stages 1–4 (or 1–6 for V1)
│   │   └── prediction_pipeline.py   # Loads model, runs inference
│   ├── entity/
│   │   ├── config_entity.py         # Dataclasses for stage configs
│   │   ├── artifact_entity.py       # Dataclasses for stage outputs
│   │   └── estimator.py             # VisaModel wrapper + TargetValueMapping
│   ├── utils/
│   │   └── main_utils.py            # YAML I/O, dill serialization, numpy helpers
│   ├── constants/
│   │   └── __init__.py              # All project-wide constants
│   ├── configuration/
│   │   ├── mongo_db_connection.py   # MongoDB client (V1)
│   │   └── aws_connection.py        # AWS S3 client (V1)
│   ├── cloud_storage/
│   │   └── aws_storage.py           # S3 upload/download (V1)
│   ├── exception/
│   │   └── __init__.py              # USvisaException with file + line info
│   └── logger/
│       └── __init__.py              # Timestamped rotating log file
├── config/
│   ├── schema.yaml                  # Column types, encoder assignments, drop cols
│   └── model.yaml                   # Model classes + GridSearchCV param grids
├── templates/
│   └── visa.html                    # FastAPI Jinja2 prediction form (V1)
├── static/css/
│   └── style.css
├── artifact/                        # Runtime-generated, gitignored
├── logs/                            # Runtime-generated, gitignored
├── notebooks/                       # EDA and feature engineering notebooks
├── flowcharts/                      # Architecture diagrams
├── .github/workflows/
│   └── cicd.yaml                    # GitHub Actions CI/CD (V1)
├── Dockerfile                       # Container definition (V1)
├── app.py                           # FastAPI application entry point (V1)
├── demo.py                          # Local pipeline runner (V3)
├── requirements.txt
├── setup.py
└── Global_Mobility_Application_Analyzer.ipynb   # Colab notebook (V2)
```

---

## Model Details

Two classifiers are evaluated in every run via `GridSearchCV` with 3-fold cross-validation scored on F1.

### KNeighborsClassifier

| Hyperparameter | Search Space |
|---|---|
| `algorithm` | `auto`, `ball_tree`, `kd_tree` |
| `weights` | `uniform`, `distance` |
| `n_neighbors` | `3`, `5`, `9` |

### RandomForestClassifier

| Hyperparameter | Search Space |
|---|---|
| `max_depth` | `10`, `15`, `20` |
| `max_features` | `sqrt`, `log2` |
| `n_estimators` | `3`, `5`, `9` |

The model with the higher cross-validated F1 score is retained. In V1, this model must also beat the currently deployed production model by at least `0.02` F1 points before it is pushed to S3.

---

## Results

| Metric | Value |
|---|---|
| Minimum accepted F1 (base threshold) | 0.60 |
| Production promotion threshold (V1) | +0.02 vs current model |
| Primary evaluation metric | F1-Score (binary) |

The model is evaluated on the held-out test set (20% of data) after SMOTEENN resampling has been applied to both train and test splits independently.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
