# 🫀 AI-Powered Heart Murmur Detection System

> An end-to-end deep learning pipeline for detecting cardiac abnormalities from raw audio recordings — bridging healthcare and Artificial Intelligence.

---

## 📌 Project Overview

This project implements a production-ready medical diagnostic system that detects heart murmurs from raw stethoscope audio recordings. By leveraging **LSTM (Long Short-Term Memory)** networks and **MFCC-based feature extraction**, the system replaces subjective manual auscultation with objective, data-driven predictions.

Built as part of the **Krish Naik Academy** guided project curriculum.

---

## 🎯 Why This Project?

| Aspect | Description |
|---|---|
| 🔊 Unstructured Audio Data | Goes beyond tabular datasets — works with raw `.wav` medical recordings |
| 🏥 Medical Domain Knowledge | Covers Systole, Diastole, and "lub-dub" cardiac cycle patterns |
| ⚠️ Real-World Challenges | Handles stethoscope noise, background artifacts, and unlabelled data |
| 🚀 Full MLOps Lifecycle | From raw data → model training → Streamlit deployment → Hugging Face hosting |

---

## 🧠 Learning Outcomes

By the end of this project, you will be able to:

- Understand **audio data structures** for machine learning
- Apply **audio preprocessing** techniques — resampling, duration normalization
- Extract features using **MFCC (Mel-Frequency Cepstral Coefficients)**
- Handle **class imbalance** in medical datasets
- Train **LSTM models** for sequence classification
- Deploy web apps using **Streamlit**
- Manage model versioning on **Hugging Face Hub**

---

## 🛠️ Tech Stack

| Category | Tools / Libraries |
|---|---|
| Language | Python |
| Deep Learning | Keras / TensorFlow |
| Audio Processing | Librosa |
| Data Manipulation | NumPy, Pandas |
| Deployment | Streamlit |
| Model Registry | Hugging Face Hub |
| Version Control | Git |
| Key Concepts | LSTM, RNN, Time-Series Classification, Class Imbalance Handling |

---

## 📚 Project Modules

### Section 1 — Project Introduction `(~36 min)`
- Use-case overview and problem framing
- Tech stack walkthrough
- Domain understanding: cardiac audio fundamentals
- Kaggle, Google Colab & Hugging Face setup
- Data import and notebook configuration

### Section 2 — Experimentation `(~79 min)`
- Best practices for ML experimentation
- Data loading and exploration (EDA)
- Audio preprocessing pipeline
- Model training and evaluation
- Prediction generation and model saving

### Section 3 — Core Software Logic & Deployment `(~44 min)`
- Project folder structure, virtual environment, Git & Hugging Face setup
- Logger and exception handling with vibe coding techniques
- Modular code implementation
- Model testing and Streamlit deployment

### Section 4 — Evaluation
- Project Quiz
- Interview Q&A

---

## 🗂️ Project Structure

```
heart-murmur-detection/
│
├── data/                   # Raw and processed audio files
├── notebooks/              # Experimentation notebooks (Colab)
├── src/
│   ├── data_loader.py      # Audio loading and preprocessing
│   ├── feature_extraction.py  # MFCC extraction
│   ├── model.py            # LSTM model definition
│   ├── train.py            # Training pipeline
│   ├── predict.py          # Inference logic
│   └── utils/
│       ├── logger.py       # Logging setup
│       └── exception.py    # Custom exception handling
├── app.py                  # Streamlit web application
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/heart-murmur-detection.git
cd heart-murmur-detection

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the App

```bash
streamlit run app.py
```

---

## 📊 Model Architecture

- **Input**: MFCC features extracted from `.wav` audio files
- **Model**: LSTM (Long Short-Term Memory) — captures temporal patterns in cardiac audio
- **Output**: Binary classification — `Murmur Present` / `No Murmur`
- **Imbalance Handling**: Class weights / oversampling techniques applied during training

---

## 🤗 Model on Hugging Face

The trained model is hosted and versioned on Hugging Face Hub.

```python
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(repo_id="<your-username>/heart-murmur-lstm", filename="model.h5")
```

---

## 📄 License

This project is for educational purposes as part of the Krish Naik Academy curriculum.

---

## 🙏 Acknowledgements

- [Krish Naik Academy](https://learn.krishnaikacademy.com) — Project guidance and curriculum
- [PhysioNet / CirCor DigiScope Dataset](https://physionet.org/) — Heart sound data
- [Librosa](https://librosa.org/) — Audio analysis library
