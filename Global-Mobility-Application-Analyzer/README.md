
# ✅ **QUIZ SET – Global Mobility Application Analyzer**

## **Quiz 1: Conceptual Understanding**

**Q1.** What is the primary objective of the Global Mobility Application Analyzer project?
a) Predict visa office location
b) Predict visa approval status
c) Predict travel duration
d) Analyze passport details

**Q2.** Which type of machine learning problem is Visa Approval Prediction?
a) Regression
b) Clustering
c) Classification
d) Recommendation

**Q3.** Which evaluation metric is best suited for this project?
a) MSE
b) Accuracy, F1-score
c) BLEU Score
d) PSNR

**Q4.** The visa features such as “Previous Travel History”, “Documents Score” are examples of:
a) Target variable
b) Features (independent variables)
c) Noise
d) Labels

**Q5.** Imbalanced datasets in visa approval classification can be handled using—
a) Oversampling
b) Undersampling
c) Class weights
d) All of the above

---

## **Quiz 2: Technical Knowledge**

**Q6.** Which algorithm is typically best for binary classification with tabular visa data?
a) CNN
b) LSTM
c) Random Forest / XGBoost
d) K-means

**Q7.** What is the purpose of one-hot encoding?
a) Reduce overfitting
b) Clean dataset
c) Convert categorical data into numerical format
d) Improve model visualization

**Q8.** What is the target column in this project?
a) Applicant Age
b) Visa Type
c) Approval Status
d) Interview Score

**Q9.** Which technique helps identify the most important visa factors?
a) PCA
b) Feature Importance
c) Clustering
d) Bagging

**Q10.** A confusion matrix helps evaluate—
a) Training time
b) Misclassification types
c) Correlation
d) Missing values

---

# ✅ **ASSIGNMENTS**

---

# **Assignment 1: Data Exploration & Cleaning**

Perform exploratory data analysis (EDA) on the dataset in the project.

### **Tasks**

1. Load the dataset and print:

   * shape
   * column names
   * missing values
   * unique value counts
2. Create visualizations:

   * Visa approval distribution
   * Correlation heatmap
   * Country vs approval rate
3. Clean the dataset by:

   * Filling or removing missing values
   * Encoding categorical variables

**Deliverables:** `.ipynb` notebook + charts + observations (short report).

---

# **Assignment 2: Feature Engineering**

Using the features in your dataset:

### **Tasks**

1. Create at least **5 new features**, e.g.:

   * Document Strength Score
   * Applicant Stability Score
   * Case Complexity Index
2. Apply scaling on numerical features.
3. Apply one-hot or label encoding wherever needed.
4. Provide explanation of **why each engineered feature matters**.

**Deliverables:**

* Python notebook
* Explanation document (1 page)

---

# **Assignment 3: Model Building & Optimization**

### **Tasks**

1. Train at least **3 ML models**:

   * Logistic Regression
   * Random Forest
   * XGBoost
2. Compare using:

   * Accuracy
   * Precision
   * Recall
   * F1-score
   * ROC-AUC
3. Perform hyperparameter tuning using **GridSearchCV / RandomizedSearchCV**.
4. Select the best model and justify your choice.

**Deliverables:**

* Code
* Model comparison table
* Best model saved as `.pkl`

---

# **Assignment 4: End-to-End Pipeline Development**

### **Tasks**

1. Build a **scikit-learn pipeline** that includes:

   * preprocessing
   * feature engineering
   * classifier
2. Use **train-test split + k-fold cross-validation**.
3. Export the pipeline for production (`joblib` or `pickle`).
4. Explain how this pipeline would work in a real visa office environment.

**Deliverables:**

* Pipeline notebook
* .pkl file
* Short explanation

---

# **Assignment 5: Model Interpretability**

### **Tasks**

1. Use **SHAP or LIME** to interpret predictions.
2. Identify the top 10 most influential visa features.
3. Analyze:

   * Why some applications get rejected
   * Which features contribute most to approvals
4. Write a 1-page insight report.

**Deliverables:**

* SHAP/LIME visualization
* Insight report

---

# **Assignment 6: Mini-Project – Build a Web App**

### **Tasks**

Build a small UI with **Streamlit** or **Flask** that accepts:

* Age
* Country of Origin
* Income
* Travel History
* Education
* Document Score
* Visa Type
* Interview Score
* etc.

Output:

* Approval Probability
* Risk Score
* Recommended Actions (auto generated)

**Deliverables:**

* app.py
* Screenshots
* Ready-to-run instructions


