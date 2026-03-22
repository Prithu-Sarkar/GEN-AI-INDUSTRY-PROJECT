# Cancer Risk Level Prediction

A multi-class machine learning system that predicts patient cancer risk — **Low**, **Medium**, or **High** — from clinical and lifestyle features. The final model is an Optuna-tuned, class-weighted XGBoost classifier tracked via MLflow on DagsHub and served through a Streamlit web application.

---

## Results

| Model | Macro-F1 | Accuracy | High-Risk Recall |
|---|---|---|---|
| Random Forest (baseline) | — | ~99%* | — |
| Logistic Regression | — | — | — |
| Random Forest + SMOTE | — | 84% | low |
| Optuna RF + SMOTE | 0.70 | — | moderate |
| Optuna XGBoost (High-Recall) | 0.50 | 61% | **0.65** |
| **Optuna Class-Weighted XGBoost** | **0.72** | **88%** | 0.45 |

> *Baseline RF achieved near-perfect accuracy due to `Overall_Risk_Score` leakage — removed in all subsequent experiments.

### Final Model — Per-Class Performance

```
              precision    recall  f1-score   support

        High       0.50      0.45      0.47        20
         Low       0.76      0.78      0.77        65
      Medium       0.92      0.92      0.92       315

    accuracy                           0.88       400
   macro avg       0.73      0.72      0.72       400
weighted avg       0.87      0.88      0.87       400
```

---

## Project Structure

```
Cancer_Risk_prediction/
├── cancer-risk-factors.csv          # Raw dataset
├── Cancer_Risk_Prediction_(ML).ipynb  # Original exploration notebook
├── Cancer_Risk_Prediction_Colab.ipynb # Final consolidated pipeline notebook
├── app.py                           # Streamlit inference application
├── main.py                          # Entry point
├── artifacts/
│   ├── final_xgb_class_weighted.pkl # Trained XGBoost model
│   ├── label_encoder.pkl            # LabelEncoder (High / Low / Medium)
│   └── feature_names.pkl            # Ordered feature column names
├── requirements.txt
└── README.md
```

---

## Dataset

**File:** `cancer-risk-factors.csv`  
**Records:** ~2,000 patients  
**Target:** `Risk_Level` — three classes: `Low`, `Medium`, `High`

### Features used for training

| Feature | Description |
|---|---|
| Age | Patient age |
| Gender | Binary encoded |
| Smoking | Smoking intensity score |
| Alcohol_Use | Alcohol consumption score |
| Obesity | Obesity score |
| Family_History | Binary family history flag |
| Diet_Red_Meat | Dietary red meat consumption |
| Diet_Salted_Processed | Dietary processed food score |
| Fruit_Veg_Intake | Fruit and vegetable intake score |
| Physical_Activity | Activity level score |
| Air_Pollution | Pollution exposure score |
| Occupational_Hazards | Occupational risk score |
| BRCA_Mutation | Binary BRCA mutation flag |
| H_Pylori_Infection | Binary H. pylori flag |
| Calcium_Intake | Calcium intake score |
| BMI | Body mass index |
| Physical_Activity_Level | Activity level (numeric) |

**Columns dropped:**
- `Patient_ID` — identifier, not a predictor
- `Cancer_Type` — outcome grouping variable, not an input
- `Overall_Risk_Score` — composite derived from the target; causes data leakage

---

## ML Pipeline

### 1. Data Ingestion
Data is pulled from **MongoDB** at runtime. If the connection fails or the collection is empty, the pipeline falls back to the local CSV automatically.

### 2. Preprocessing
- Stratified 80/20 train/test split (`random_state=42`)
- No feature scaling needed — all models are tree-based
- `LabelEncoder` applied to the target variable

### 3. Class Imbalance Strategy

Two strategies were evaluated:

**SMOTE** — Synthetic Minority Over-Sampling applied inside `ImbPipeline` on each CV fold to prevent data leakage.

**Class Weights** — Per-sample weights inversely proportional to class frequency, passed directly to XGBoost's `sample_weight` parameter. This was the winning approach.

```python
weight(class c) = max(class_count) / count(c)
```

### 4. Hyperparameter Optimisation — Optuna

Both Random Forest and XGBoost were tuned using **Optuna** with the **TPE (Tree-structured Parzen Estimator)** sampler — a Bayesian optimisation strategy that models the distribution of good hyperparameter configurations over successive trials.

Two XGBoost studies were run:
- **High-Recall objective** — maximise recall for the `High` class (clinical safety focus)
- **Macro-F1 objective** — balance performance across all three classes (final winner)

### 5. Final Model

**Optuna-tuned Class-Weighted XGBoost** with macro-F1 as the optimisation objective and 40 Optuna trials.

```python
XGBClassifier(
    objective    = 'multi:softmax',
    eval_metric  = 'mlogloss',
    n_estimators = <optuna_best>,
    max_depth    = <optuna_best>,
    learning_rate= <optuna_best>,
    subsample    = <optuna_best>,
    colsample_bytree = <optuna_best>,
    gamma        = <optuna_best>,
    reg_alpha    = <optuna_best>,
    reg_lambda   = <optuna_best>,
    sample_weight = inverse_frequency_weights
)
```

---

## Experiment Tracking

All runs are logged to **MLflow** on **DagsHub**.

Each run records:
- `macro_f1` — primary optimisation metric
- `high_recall` — recall for the High-risk class
- Hyperparameters
- Model artifact (final XGBoost run only)
- EDA and evaluation plots

**Experiment name:** `Cancer_Risk_Prediction`  
**Runs logged:** baseline RF, baseline LR, SMOTE RF, Optuna RF, Optuna XGB High-Recall, Final Class-Weighted XGBoost

---

## Streamlit App

The trained model is served through a Streamlit web application (`app.py`) that supports two prediction modes:

**Batch mode** — upload a CSV with feature columns, get predictions + class probabilities for every row, downloadable as CSV.

**Manual mode** — enter patient features via sidebar sliders and get an instant prediction with a probability breakdown and a clinical flag if High-risk probability ≥ 0.5.

```bash
streamlit run app.py
```

> Ensure `final_xgb_class_weighted.pkl`, `label_encoder.pkl`, and `feature_names.pkl` are in the working directory.

---

## Setup

### Prerequisites

```bash
pip install -r requirements.txt
```

```
streamlit
pandas
numpy
joblib
xgboost
scikit-learn
imbalanced-learn
optuna
mlflow
pymongo
dagshub
```

### Environment Variables

| Variable | Description |
|---|---|
| `MONGO_DB_URL` | MongoDB connection string |
| `MLFLOW_TRACKING_URI` | DagsHub MLflow tracking URI |
| `MLFLOW_TRACKING_USERNAME` | DagsHub username |
| `MLFLOW_TRACKING_PASSWORD` | DagsHub access token |

Set these as environment variables or, when running in Google Colab, store them as **Colab Secrets**.

### Running the Pipeline

Open `Cancer_Risk_Prediction_Colab.ipynb` and run all cells top to bottom. The notebook handles installation, data ingestion, training, evaluation, MLflow logging, artifact saving, and output packaging automatically.

---

## Key Design Decisions

**Why XGBoost over Random Forest?**  
XGBoost with class weighting outperformed all Random Forest variants on macro-F1 while achieving better calibration across minority classes.

**Why class weights instead of SMOTE for the final model?**  
SMOTE introduces synthetic samples that can distort the feature space in small datasets. Class weighting achieves similar imbalance correction without modifying the training distribution.

**Why macro-F1 as the optimisation objective?**  
Macro-F1 penalises poor performance on any single class equally, making it more appropriate than accuracy or weighted-F1 for imbalanced multi-class problems where the minority class (High risk) carries the most clinical significance.

**Why was `Overall_Risk_Score` dropped?**  
It is a composite feature derived from the target variable, making it a direct source of data leakage. Models trained with it achieved near-perfect accuracy (>99%) but would fail entirely on real-world data.

---

## License

MIT
