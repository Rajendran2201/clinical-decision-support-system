import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import os
import joblib

def create_targets(datasets, cutoff_date='2022-01-01'):
    """
    Creates target labels based on whether the patient has 
    an inpatient encounter after the cutoff date.
    """
    e = datasets['encounters'].copy()
    e['START'] = pd.to_datetime(e['START'])
    
    # Positive class: patients with inpatient visits after cutoff
    high_risk_patients = e[(e['START'] >= cutoff_date) & 
                           (e['ENCOUNTERCLASS'].isin(['inpatient', 'emergency']))]['PATIENT'].unique()
    
    # All patients
    all_patients = datasets['patients']['Id'].unique()
    
    targets = pd.DataFrame({'PATIENT': all_patients})
    targets['Target'] = targets['PATIENT'].isin(high_risk_patients).astype(int)
    return targets.set_index('PATIENT')

def train_risk_model(X, y, output_dir):
    """
    Trains an XGBoost model and saves evaluation plots.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluation
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    print("\n--- Model Evaluation ---")
    print(classification_report(y_test, preds))
    auc = roc_auc_score(y_test, probs)
    print(f"ROC-AUC Score: {auc:.4f}")
    
    # 1. Confusion Matrix Plot
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, preds)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()
    
    # 2. ROC Curve Plot
    plt.figure(figsize=(8, 6))
    fpr, tpr, _ = roc_curve(y_test, probs)
    plt.plot(fpr, tpr, label=f'XGBoost (AUC = {auc:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'roc_curve.png'))
    plt.close()
    
    # Save model natively for cross-version compatibility
    model_path = os.path.join(os.path.dirname(output_dir), 'src', 'risk_model.json')
    model.save_model(model_path)
    
    # SHAP Explainability
    try:
        # Use a more robust explainer initialization
        explainer = shap.Explainer(model)
        shap_values = explainer(X_test)
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test, show=False)
        plt.title('SHAP Feature Importance')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'shap_summary.png'))
        plt.close()
    except Exception as e:
        print(f"Warning: SHAP explainability plot failed: {e}")
        # Create a placeholder or skip
    
    return model, None

if __name__ == "__main__":
    from preprocessing import load_data, clean_data
    from feature_engineering import create_patient_features
    
    DATA_DIR = "/Users/rajendran/Desktop/cdss/data"
    VIS_DIR = "/Users/rajendran/Desktop/cdss/visualizations"
    
    datasets = load_data(DATA_DIR)
    datasets = clean_data(datasets)
    
    # For training, we generate features up to 2022
    features = create_patient_features(datasets)
    targets = create_targets(datasets, cutoff_date='2022-01-01')
    
    # Join features and targets
    df = features.join(targets, how='inner')
    X = df.drop(columns=['Target'])
    y = df['Target']
    
    print(f"Training on {len(df)} samples, target distribution:\n{y.value_counts()}")
    
    model, explainer = train_risk_model(X, y, VIS_DIR)
    print("Model training and explainability charts complete.")
