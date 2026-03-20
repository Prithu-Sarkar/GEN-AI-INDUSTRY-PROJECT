
import streamlit as st
import pandas as pd
import joblib
import os

BASE_DIR    = "/content/thunderstorm_forecasting"
MODEL_PATH  = f"{BASE_DIR}/models/best_model_Random_Forest.pkl"
SCALER_PATH = f"{BASE_DIR}/models/scaler.pkl"

FEATURE_COLS = [
    "SWEAT index", "Showalter index", "LIFTED index", "K index",
    "Cross totals index", "Vertical totals index", "Totals totals index",
    "TLCL", "PLCL", "CINE", "CAPE", "PRECIPITABLE WATER"
]

@st.cache_resource
def load_artifacts():
    return joblib.load(MODEL_PATH), joblib.load(SCALER_PATH)

model, scaler = load_artifacts()

st.set_page_config(page_title="Thunderstorm Forecasting", page_icon="⛈️", layout="wide")
st.title("⛈️ Thunderstorm Forecasting System")
st.markdown("Enter atmospheric index values to predict thunderstorm occurrence.")

st.sidebar.header("📊 Input Atmospheric Indices")
defaults = {
    "SWEAT index": 80.0, "Showalter index": 5.0, "LIFTED index": 0.0,
    "K index": 20.0, "Cross totals index": 20.0, "Vertical totals index": 25.0,
    "Totals totals index": 45.0, "TLCL": 280.0, "PLCL": 900.0,
    "CINE": -10.0, "CAPE": 100.0, "PRECIPITABLE WATER": 30.0
}
input_vals = {feat: st.sidebar.number_input(feat, value=float(v), format="%.2f")
              for feat, v in defaults.items()}

if st.sidebar.button("🔍 Predict Thunderstorm", use_container_width=True):
    import pandas as pd
    input_df    = pd.DataFrame([input_vals])
    input_sc    = scaler.transform(input_df[FEATURE_COLS])
    pred        = model.predict(input_sc)[0]
    prob        = model.predict_proba(input_sc)[0]
    col1, col2  = st.columns(2)
    with col1:
        st.error("⛈️ THUNDERSTORM PREDICTED") if pred == 1 else st.success("☀️ NO THUNDERSTORM PREDICTED")
    with col2:
        st.metric("Thunderstorm Probability",    f"{prob[1]*100:.1f}%")
        st.metric("No-Thunderstorm Probability", f"{prob[0]*100:.1f}%")
    st.subheader("Input Summary")
    st.dataframe(input_df, use_container_width=True)

st.divider()
st.caption("Model: Random Forest | SMOTE | MLflow / DagsHub")
