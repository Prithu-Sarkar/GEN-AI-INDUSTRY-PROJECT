# Books Recommender System

A modular, end-to-end collaborative filtering recommendation system built with Python. The system ingests raw book-rating data, processes it through a structured ML pipeline, trains a K-Nearest Neighbours model, and serves recommendations through a Streamlit web application. Experiment tracking is handled via MLflow with optional DagsHub integration.

---

## Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Dataset](#dataset)
- [Version A — Local / Docker Deployment](#version-a--local--docker-deployment)
- [Version B — Notebook Execution](#version-b--notebook-execution)
- [Pipeline Stages](#pipeline-stages)
- [MLflow Tracking](#mlflow-tracking)
- [Artifacts](#artifacts)
- [Configuration Reference](#configuration-reference)

---

## Architecture

```
Training Pipeline                         Inference Application
─────────────────                         ──────────────────────
Data Source (CSV)                         Streamlit Web App
      │                                         │
      ▼                                         ▼
Data Ingestion                        Recommendation Engine ──► Poster API
      │                                    ▲         ▲
      ▼                                    │         │
Data Validation                            │         │
      │                               Artifacts Store
      ▼                                    ▲
Data Transformation                        │
      │                                    │
      ▼                                    │
Model Trainer ─────────────────────────────┘
```

The training pipeline produces three serialised objects (`book_names.pkl`, `book_pivot.pkl`, `final_rating.pkl`) and a trained model (`model.pkl`), all stored under `artifacts/`. The inference layer reads directly from those artifacts at runtime.

---

## Project Structure

```
books_recommender_project/
│
├── books_recommender/                  # Core Python package
│   ├── components/
│   │   ├── stage_00_data_ingestion.py
│   │   ├── stage_01_data_validation.py
│   │   ├── stage_02_data_transformation.py
│   │   └── stage_03_model_trainer.py
│   ├── config/
│   │   └── configuration.py
│   ├── constant/
│   │   └── __init__.py
│   ├── entity/
│   │   └── config_entity.py
│   ├── exception/
│   │   └── exception_handler.py
│   ├── logger/
│   │   └── log.py
│   ├── pipeline/
│   │   └── training_pipeline.py
│   └── utils/
│       └── util.py
│
├── config/
│   └── config.yaml                     # All path and parameter configuration
│
├── artifacts/                          # Auto-generated; all pipeline outputs
│   ├── dataset/
│   │   ├── ingested_data/              # Raw CSVs after ingestion
│   │   ├── clean_data/                 # Validated & merged dataset
│   │   └── transformed_data/           # Pivot table (transformed_data.pkl)
│   ├── serialized_objects/             # book_names.pkl, book_pivot.pkl, final_rating.pkl
│   └── trained_model/                  # model.pkl
│
├── logs/                               # Timestamped log files
├── notebook/                           # EDA charts and notebook outputs
├── app.py                              # Streamlit application
├── main.py                             # CLI entry point for training
├── setup.py
├── requirements.txt
└── Dockerfile
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| ML Model | Scikit-learn `NearestNeighbors` (cosine, brute-force) |
| Data Processing | Pandas, NumPy, SciPy (sparse matrix) |
| Web Application | Streamlit |
| Experiment Tracking | MLflow + DagsHub |
| Configuration | PyYAML |
| Containerisation | Docker |
| Serialisation | Pickle |

---

## Dataset

Three CSV files from the [Book-Crossing Dataset](http://www2.informatik.uni-freiburg.de/~cziegler/BX/):

| File | Description |
|---|---|
| `BX-Books.csv` | Book metadata — title, author, year, publisher, cover image URL |
| `BX-Book-Ratings.csv` | User–book ratings (scale 0–10) |
| `BX-Users.csv` | User demographic information |

**Filtering criteria applied during validation:**

- Users retained only if they have rated more than **200 books**
- Books retained only if they have received at least **50 ratings**
- Duplicate `(user_id, title)` pairs removed

---

## Version A — Local / Docker Deployment

### Prerequisites

- Python 3.8+
- Docker (for containerised run)
- DagsHub account (optional, for remote MLflow tracking)

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd books_recommender_project

pip install -r requirements.txt
pip install -e .
```

### 2. Set Environment Variables

Create a `.env` file or export directly:

```bash
# MongoDB (if used for data source)
export MONGO_DB_URL="your_mongodb_connection_string"

# MLflow — DagsHub (recommended)
export MLFLOW_TRACKING_URI="https://dagshub.com/<username>/<repo>.mlflow"
export MLFLOW_TRACKING_USERNAME="your_dagshub_username"
export MLFLOW_TRACKING_PASSWORD="your_dagshub_token"

# MLflow — local fallback
# export MLFLOW_TRACKING_URI="file://$(pwd)/mlruns"
```

### 3. Place Dataset Files

Copy your three CSV files into the ingested data directory before running the pipeline, or let the pipeline pull from the configured download URL in `config/config.yaml`:

```bash
mkdir -p artifacts/dataset/ingested_data
cp /path/to/BX-Books.csv          artifacts/dataset/ingested_data/
cp /path/to/BX-Book-Ratings.csv   artifacts/dataset/ingested_data/
cp /path/to/BX-Users.csv          artifacts/dataset/ingested_data/
```

### 4. Run the Training Pipeline

```bash
python main.py
```

This executes all four pipeline stages in sequence and logs parameters, metrics, and the model to MLflow.

### 5. Launch the Streamlit App

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser. Select a book from the dropdown and click **Show Recommendation** to see five similar books with cover images.

To re-train from within the UI, click **Train Recommender System**.

---

### Docker Deployment

#### Build the Image

```bash
docker build -t books-recommender:latest .
```

#### Run the Container

```bash
docker run -p 8501:8501 \
  -e MONGO_DB_URL="your_mongodb_connection_string" \
  -e MLFLOW_TRACKING_URI="https://dagshub.com/<username>/<repo>.mlflow" \
  -e MLFLOW_TRACKING_USERNAME="your_dagshub_username" \
  -e MLFLOW_TRACKING_PASSWORD="your_dagshub_token" \
  books-recommender:latest
```

The application will be available at `http://localhost:8501`.

#### Mount Artifacts (Optional)

To persist artifacts across container restarts, mount a local volume:

```bash
docker run -p 8501:8501 \
  -v $(pwd)/artifacts:/app/artifacts \
  -e MLFLOW_TRACKING_URI="..." \
  books-recommender:latest
```

---

## Version B — Notebook Execution

This version runs the entire pipeline inside a single Jupyter notebook (`books_recommender.ipynb`). No Docker or local Python environment setup is required.

### Prerequisites

- A Jupyter-compatible environment (JupyterLab, VS Code, or any hosted notebook service)
- The three dataset CSV files accessible on disk
- Secrets configured in your environment (see below)

### 1. Configure Secrets

The notebook reads credentials from environment secrets rather than hardcoded values. Set the following secrets in your environment before opening the notebook:

| Secret Key | Description |
|---|---|
| `MONGO_DB_URL` | MongoDB connection string |
| `MLFLOW_TRACKING_URI` | MLflow tracking server URI |
| `MLFLOW_TRACKING_USERNAME` | MLflow / DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | MLflow / DagsHub token or password |

To use local MLflow instead of DagsHub, set `USE_DAGSHUB = False` in the notebook's environment cell. Logs will be written to `./mlruns/`.

### 2. Place Dataset Files

The notebook expects the three CSV files at the following paths. Update these paths in **Step 5** of the notebook if your files are stored elsewhere:

```
/path/to/BX-Books.csv
/path/to/BX-Book-Ratings.csv
/path/to/BX-Users.csv
```

A verification cell checks all three files are present and prints their sizes before the pipeline runs.

### 3. Run the Notebook

Execute cells top to bottom. Each step is self-contained:

| Step | Description |
|---|---|
| 0 | Install dependencies |
| 1 | Set environment variables from secrets |
| 2 | Create project directory structure |
| 3 | Write all source files to disk (logger, exception, config, entity, all stages, pipeline) |
| 4 | Install `books_recommender` package in editable mode |
| 5 | Verify dataset files are present |
| 6 | Run the full training pipeline |
| 7 | Print artifact directory tree with file sizes |
| 8 | Load artifacts and run the recommendation engine |
| 9 | Generate EDA charts (rating distribution, top-rated books) |
| 10 | Package the entire project as a downloadable ZIP |

### 4. Run Recommendations

After training completes (Step 6), Step 8 loads all artifacts and exposes a `recommend_book()` function. The following cell displays ten books from the catalog with their index numbers:

```
📚 10 books from the catalog — pick one by index:
─────────────────────────────────────────────────────────────────
  [0]  The Lovely Bones: A Novel
  [1]  Harry Potter and the Sorcerer's Stone
  [2]  The Da Vinci Code
  ...
─────────────────────────────────────────────────────────────────
```

Change `SELECTED_INDEX` to any number 0–9 and re-run the cell to get five similar book recommendations with their cover image URLs.

### 5. Export the Project

Step 10 packages the full project — source code, artifacts, logs, and EDA charts — into a ZIP file saved at the working directory root. Download it from the file browser panel.

---

## Pipeline Stages

### Stage 00 — Data Ingestion

Copies or downloads the raw CSV files into `artifacts/dataset/ingested_data/`. In the notebook version, files are read from their local paths. In the local/Docker version, data can be fetched from the URL configured in `config.yaml`.

**Output:** `artifacts/dataset/ingested_data/BX-Books.csv`, `BX-Book-Ratings.csv`, `BX-Users.csv`

### Stage 01 — Data Validation

Reads the raw CSVs, applies filtering rules, merges ratings with book metadata, and saves the cleaned dataset. Also serialises `final_rating.pkl` for use by the recommendation engine.

**Output:** `artifacts/dataset/clean_data/clean_data.csv`, `artifacts/serialized_objects/final_rating.pkl`

### Stage 02 — Data Transformation

Constructs a user–book pivot table (rows = book titles, columns = user IDs, values = ratings), fills missing values with zero, and serialises the pivot table and book name index.

**Output:** `artifacts/dataset/transformed_data/transformed_data.pkl`, `artifacts/serialized_objects/book_names.pkl`, `artifacts/serialized_objects/book_pivot.pkl`

### Stage 03 — Model Trainer

Converts the pivot table to a sparse matrix, fits a `NearestNeighbors` model with cosine similarity and brute-force search, logs parameters and metrics to MLflow, and saves the model locally.

**Logged to MLflow:**

| Type | Key | Value |
|---|---|---|
| Parameter | `algorithm` | `brute` |
| Parameter | `metric` | `cosine` |
| Parameter | `n_neighbors` | `6` |
| Parameter | `pivot_shape` | `(n_books, n_users)` |
| Metric | `n_books` | Number of unique books in pivot |
| Metric | `n_users` | Number of unique users in pivot |

**Output:** `artifacts/trained_model/model.pkl`

---

## MLflow Tracking

All training runs are tracked under the experiment name `books_recommender`.

**DagsHub (remote):**

```
MLFLOW_TRACKING_URI = https://dagshub.com/<username>/<repo>.mlflow
```

Log in to DagsHub and navigate to the Experiments tab to view run history, compare parameters, and inspect logged model artifacts.

**Local:**

```
MLFLOW_TRACKING_URI = file://<project_root>/mlruns
```

Launch the MLflow UI locally:

```bash
mlflow ui --backend-store-uri ./mlruns
```

Open `http://localhost:5000`.

---

## Artifacts

All pipeline outputs are written under `artifacts/` and are git-ignored by default. The directory is auto-created on first run.

```
artifacts/
├── dataset/
│   ├── ingested_data/          Raw CSVs
│   ├── clean_data/             clean_data.csv
│   └── transformed_data/       transformed_data.pkl
├── serialized_objects/
│   ├── book_names.pkl
│   ├── book_pivot.pkl
│   └── final_rating.pkl
└── trained_model/
    └── model.pkl
```

---

## Configuration Reference

All pipeline paths and parameters are centralised in `config/config.yaml`. No path is hardcoded in any source file.

```yaml
artifacts_config:
  artifacts_dir: artifacts               # Root output directory

data_ingestion_config:
  dataset_download_url: <url>            # Fallback download source
  dataset_dir: dataset
  ingested_dir: ingested_data
  raw_data_dir: raw_data

data_validation_config:
  clean_data_dir: clean_data
  serialized_objects_dir: serialized_objects
  books_csv_file: BX-Books.csv
  ratings_csv_file: BX-Book-Ratings.csv

data_transformation_config:
  transformed_data_dir: transformed_data

model_trainer_config:
  trained_model_dir: trained_model
  trained_model_name: model.pkl

recommendation_config:
  poster_api_url: <poster_api_endpoint>
```

To change any output directory or file name, edit `config.yaml` only — the rest of the codebase picks up changes automatically through `AppConfiguration`.

---

## Logging

Each run generates a timestamped log file under `logs/`:

```
logs/log_2025-06-01-14-32-10.log
```

Log entries capture stage start/end markers, dataset shapes, file paths, and any exceptions with full traceback including the source file and line number.
