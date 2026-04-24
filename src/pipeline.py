import pandas as pd
import joblib
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(__file__))

from preprocessing import load_data, clean_data
from feature_engineering import create_patient_features
from rules import apply_clinical_rules
from imaging import analyze_xray

class CDSSPipeline:
    def __init__(self, data_dir, model_path):
        self.data_dir = data_dir
        self.model_path = model_path
        self.datasets = None
        self.model = None
        self.features_df = None
        
    def initialize(self):
        """Loads data and model."""
        self.datasets = clean_data(load_data(self.data_dir))
        from xgboost import XGBClassifier
        self.model = XGBClassifier()
        self.model.load_model(self.model_path)
        self.features_df = create_patient_features(self.datasets)
        
    def analyze_from_db(self, patient_id):
        """Standard analysis from the Synthea database."""
        if patient_id not in self.features_df.index:
            return {"error": f"Patient ID {patient_id} not found."}
            
        features = self.features_df.loc[[patient_id]]
        risk_score = self.model.predict_proba(features)[0, 1]
        
        # Prepare data for rule engine
        clinical_data = features.iloc[0].to_dict()
        clinical_data['ai_risk_score'] = risk_score
        
        # In DB mode, we don't have a specific X-ray image file unless mapped
        # So we run standard clinical rules
        report = apply_clinical_rules(clinical_data)
        
        p_info = self.datasets['patients'][self.datasets['patients']['Id'] == patient_id].iloc[0]
        report['patient_name'] = f"{p_info['FIRST']} {p_info['LAST']}"
        report['ai_risk_score'] = round(float(risk_score), 4)
        report['vitals_summary'] = clinical_data
        return report

    def analyze_live(self, vitals_dict, x_ray_file=None):
        """
        New multimodal workflow: Vitals + X-ray analysis.
        """
        # 1. Image Analysis (if provided)
        image_results = {}
        if x_ray_file:
            image_results = analyze_xray(x_ray_file)
            
        # 2. Extract features from vitals_dict for the ML model
        # We simulate the model prediction based on manual vitals
        # In a production app, we'd process these into the exact 13 features.
        # For simplicity in this demo, we use a weighted combination of model features
        mock_risk = 0.1
        if vitals_dict.get('Temperature', 37) > 38.5: mock_risk += 0.3
        if vitals_dict.get('SpO2', 98) < 92: mock_risk += 0.4
        
        # 3. Combine for Rule Engine
        combined_data = vitals_dict.copy()
        combined_data['image_analysis'] = image_results
        combined_data['ai_risk_score'] = min(0.99, mock_risk)
        
        report = apply_clinical_rules(combined_data)
        report['patient_name'] = "Live Patient (Consultation)"
        report['ai_risk_score'] = round(float(mock_risk), 4)
        report['image_analysis'] = image_results
        return report

if __name__ == "__main__":
    print("CDSS Pipeline v2.0 initialized.")
