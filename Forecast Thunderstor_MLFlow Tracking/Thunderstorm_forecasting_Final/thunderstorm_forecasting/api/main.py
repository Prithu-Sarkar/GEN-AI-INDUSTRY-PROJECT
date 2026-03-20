
from fastapi import FastAPI
from pydantic import BaseModel
import joblib, numpy as np

BASE_DIR = "/content/thunderstorm_forecasting"
model  = joblib.load(f"{BASE_DIR}/models/best_model_Random_Forest.pkl")
scaler = joblib.load(f"{BASE_DIR}/models/scaler.pkl")

app = FastAPI(title="Thunderstorm Forecasting API")

class Features(BaseModel):
    sweat_index: float; showalter_index: float; lifted_index: float
    k_index: float; cross_totals: float; vertical_totals: float
    totals_totals: float; tlcl: float; plcl: float
    cine: float; cape: float; precipitable_water: float

COLS = ["sweat_index","showalter_index","lifted_index","k_index",
        "cross_totals","vertical_totals","totals_totals",
        "tlcl","plcl","cine","cape","precipitable_water"]

@app.get("/")
def root(): return {"message": "Thunderstorm Forecasting API — POST /predict"}

@app.post("/predict")
def predict(data: Features):
    x = np.array([[getattr(data, c) for c in COLS]])
    pred = int(model.predict(scaler.transform(x))[0])
    prob = float(model.predict_proba(scaler.transform(x))[0][1])
    return {"prediction": pred,
            "label": "THUNDERSTORM" if pred else "NO THUNDERSTORM",
            "probability_thunderstorm": prob}
