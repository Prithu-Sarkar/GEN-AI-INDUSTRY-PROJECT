# Social Video Audience Sentiment Intelligence - Assignments & Quizzes

Welcome to the learning module for the Social Video Audience Sentiment Intelligence project! This document contains quizzes to test your understanding and practical assignments to help you extend the project.

---

## Part 1: Quizzes

### Topic 1: Project Architecture & DVC

**Q1. What is the primary purpose of `dvc.yaml` in this project?**
- [ ] To define the Flask API routes.
- [ ] To manage the Chrome Extension manifest.
- [ ] To define the machine learning pipeline stages and dependencies.
- [ ] To store the raw dataset.

**Q2. Which command is used to reproduce the entire pipeline defined in `dvc.yaml`?**
- [ ] `python main.py`
- [ ] `dvc repro`
- [ ] `git commit`
- [ ] `pip install -r requirements.txt`

**Q3. In the architecture, how does the Chrome Extension communicate with the ML model?**
- [ ] It loads the `.pkl` files directly in the browser.
- [ ] It sends HTTP requests to the Flask API.
- [ ] It reads from the `data/` directory.
- [ ] It connects directly to the DVC remote storage.

### Topic 2: Machine Learning Concepts

**Q4. What technique is used to convert text data into numerical features in this project?**
- [ ] One-Hot Encoding
- [ ] Word2Vec
- [ ] TF-IDF (Term Frequency-Inverse Document Frequency)
- [ ] BERT Embeddings

**Q5. Which algorithm is used for the sentiment classification model?**
- [ ] Random Forest
- [ ] LightGBM (Light Gradient Boosting Machine)
- [ ] Logistic Regression
- [ ] Support Vector Machine (SVM)

**Q6. Why do we save the `tfidf_vectorizer.pkl` artifact?**
- [ ] To visualize the word clouds.
- [ ] To transform new, unseen text data into the same feature space as the training data during inference.
- [ ] To reduce the size of the model file.
- [ ] It is not necessary for inference.

### Topic 3: Deployment & Integration

**Q7. What file is the entry point for the Flask API?**
- [ ] `src/model/model_building.py`
- [ ] `flask_api/main.py`
- [ ] `yt-chrome-plugin-frontend/popup.js`
- [ ] `dvc.lock`

**Q8. In the Chrome Extension, which file is responsible for handling the user's click event and sending the comment to the API?**
- [ ] `manifest.json`
- [ ] `popup.html`
- [ ] `popup.js`
- [ ] `style.css`

---

## Part 2: Practical Assignments

### Assignment 1: Model Improvement
**Objective:** Improve the model's performance or experiment with different algorithms.

**Tasks:**
1.  **Explore Data:** Analyze the `data/raw` dataset. Are the classes balanced?
2.  **Feature Engineering:** Try using `CountVectorizer` instead of `TfidfVectorizer` in `src/model/model_building.py`. Compare the results.
3.  **Model Selection:** Replace LightGBM with a `RandomForestClassifier` from scikit-learn. Train the model and evaluate its accuracy.
4.  **Hyperparameter Tuning:** Add a new parameter to `params.yaml` for the model (e.g., `n_estimators` for Random Forest) and use it in the training script.

### Assignment 2: API Extension
**Objective:** enhance the backend capabilities.

**Tasks:**
1.  **Batch Prediction:** Modify `flask_api/main.py` to accept a list of comments instead of a single comment.
2.  **Response Format:** Update the API to return not just the sentiment label, but also the prediction probability (confidence score).
3.  **Logging:** Implement a logging mechanism in the API to save every incoming request and its prediction to a file (e.g., `api_logs.csv`) for monitoring.

### Assignment 3: Frontend Enhancement
**Objective:** Improve the user experience of the Chrome Extension.

**Tasks:**
1.  **UI Polish:** Modify `yt-chrome-plugin-frontend/popup.html` and `css` to make the popup look more modern (e.g., add a loading spinner while waiting for the API response).
2.  **Error Handling:** Update `popup.js` to gracefully handle cases where the API is down or returns an error, displaying a user-friendly message.
3.  **Confidence Display:** If you completed Assignment 2 (Response Format), update the frontend to display the confidence score alongside the sentiment prediction (e.g., "Positive (85%)").

---

