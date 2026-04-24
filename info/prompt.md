You are an expert AI/ML engineer and healthcare data scientist. I want you to build a complete end-to-end Clinical Decision Support System (CDSS) using multiple healthcare CSV datasets.

## 🎯 Objective

Build a Patient Risk Prediction and Clinical Alert System that:

1. Predicts high-risk patients (e.g., hospitalization risk in next 30 days)
2. Generates clinical alerts using rule-based logic
3. Provides actionable recommendations
4. Has a simple Streamlit UI for interaction            

---

## 📂 Datasets Available

I have the following CSV files:

* patients.csv
* encounters.csv
* conditions.csv
* observations.csv
* allergies.csv
* careplans.csv
* immunizations.csv
* devices.csv
* organizations.csv
* payers.csv
* labels.csv (optional for advanced multimodal model)

All datasets are linked via:

* PATIENT ID
* ENCOUNTER ID

---

## ⚙️ Requirements

### 1. Data Preprocessing

* Load all datasets using pandas
* Handle missing values appropriately
* Convert date columns to datetime
* Ensure consistent column naming (PATIENT, ENCOUNTER)
* Remove duplicates

---

### 2. Data Integration

* Merge datasets to create a **master patient-level dataset**
* Aggregate data so that each row represents one patient
* Use grouping and aggregation techniques

---

### 3. Feature Engineering

Create meaningful features:

#### Demographic

* Age
* Gender (encoded)

#### Encounter-based

* Total encounters
* Encounters in last 30 days
* Inpatient visit count

#### Clinical

* Number of conditions
* Chronic condition flags
* Observation statistics (mean, max, latest)

#### Risk indicators

* Allergy count
* Device usage
* Immunization count

#### Financial

* Total healthcare cost
* Average cost per encounter

---

### 4. Target Variable Creation

Define a binary target:

* 1 → Patient has inpatient encounter in next 30 days
* 0 → Otherwise

Explain clearly how to construct this using encounter dates.

---

### 5. Model Development

Train the following models:

* Logistic Regression (baseline)
* Random Forest
* XGBoost (primary model)

Include:

* Train-test split
* Model training
* Performance evaluation (Accuracy, Precision, Recall, ROC-AUC)

---

### 6. Model Explainability

* Use SHAP to explain predictions
* Show feature importance

---

### 7. Rule-Based Clinical Engine

Implement rules such as:

* High visit frequency → Alert
* High observation values → Alert
* High allergy count → Alert
* Missing immunizations → Alert

Map alerts to recommendations.

---

### 8. Final Prediction Pipeline

Create a function:

predict_patient(patient_id)

That:

1. Fetches patient data
2. Generates features
3. Predicts risk score
4. Applies rule engine
5. Returns:

   * Risk score
   * Risk level
   * Alerts
   * Recommendations

---

### 9. Streamlit UI

Build a simple UI:

* Input: Patient ID
* Output:

  * Risk score
  * Risk category
  * Alerts
  * Recommendations

---

### 10. Code Structure

Organize code into modules:

* preprocessing.py
* feature_engineering.py
* model.py
* rules.py
* app.py

---

### 11. Advanced (Optional)

* Add clustering (K-Means) for patient segmentation
* Integrate labels.csv for image-based model (CNN)
* Combine clinical + image predictions

---

## 📦 Output Expectations

Provide:

1. Clean, modular Python code
2. Explanation for each step
3. Comments in code
4. Best practices
5. Suggestions for improvement

---

## ⚠️ Constraints

* Use Python only
* Use pandas, sklearn, xgboost, shap, streamlit
* Keep code beginner-friendly but professional
* Avoid unnecessary complexity

---

Now start step-by-step:

1. First implement data loading and preprocessing
2. Then proceed sequentially through all steps
3. Ensure everything is runnable

Do NOT skip steps. Build this like a real production-ready project.
