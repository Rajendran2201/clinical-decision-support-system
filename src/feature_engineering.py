import pandas as pd
import numpy as np

def create_patient_features(datasets):
    """
    Creates a patient-level feature set from the various datasets.
    """
    p = datasets['patients'].copy()
    e = datasets['encounters'].copy()
    c = datasets['conditions'].copy()
    o = datasets['observations'].copy()
    
    # 1. Base Demographic Features
    # Age calculation (assuming reference date is current time or late 2024/2026)
    p['BIRTHDATE'] = pd.to_datetime(p['BIRTHDATE'])
    p['Age'] = 2026 - p['BIRTHDATE'].dt.year
    p['IsMale'] = (p['GENDER'] == 'M').astype(int)
    
    patient_df = p[['Id', 'Age', 'IsMale', 'HEALTHCARE_EXPENSES', 'HEALTHCARE_COVERAGE']].rename(columns={'Id': 'PATIENT'})
    patient_df = patient_df.set_index('PATIENT')
    
    # 2. Encounter Features
    e_counts = e.groupby('PATIENT').size().rename('TotalEncounters')
    e_inpatient = e[e['ENCOUNTERCLASS'] == 'inpatient'].groupby('PATIENT').size().rename('InpatientEncounters')
    e_emergency = e[e['ENCOUNTERCLASS'] == 'emergency'].groupby('PATIENT').size().rename('EmergencyEncounters')
    
    patient_df = patient_df.join(e_counts).join(e_inpatient).join(e_emergency).fillna(0)
    
    # 3. Condition Features
    c_counts = c.groupby('PATIENT').size().rename('ConditionCount')
    # Flag for some chronic diseases (example: Diabetes, Hypertension)
    c['IsDiabetes'] = c['DESCRIPTION'].str.contains('diabetes', case=False).astype(int)
    c['IsHypertension'] = c['DESCRIPTION'].str.contains('hypertension', case=False).astype(int)
    
    c_flags = c.groupby('PATIENT').agg({'IsDiabetes': 'max', 'IsHypertension': 'max'})
    
    patient_df = patient_df.join(c_counts).join(c_flags).fillna(0)
    
    # 4. Observation Features (Latest Vitals)
    # We focus on the most recent values for specific LOINC codes
    # For simplicity, we'll take specific common descriptions
    vitals = ['Body Height', 'Body Weight', 'Body Mass Index', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Heart rate']
    
    for vital in vitals:
        # Get latest observation for each patient for this vital
        latest_obs = o[o['DESCRIPTION'].str.contains(vital, case=False)].sort_values('DATE').groupby('PATIENT').last()
        if not latest_obs.empty:
            # Note: VALUE in Synthea is usually numeric but stored as object in raw CSV
            patient_df[vital.replace(' ', '')] = pd.to_numeric(latest_obs['VALUE'], errors='coerce')
            
    return patient_df.fillna(patient_df.mean())

if __name__ == "__main__":
    from preprocessing import load_data, clean_data
    datasets = load_data("/Users/rajendran/Desktop/cdss/data")
    datasets = clean_data(datasets)
    features = create_patient_features(datasets)
    print(f"Feature set created: {features.shape}")
    print(features.head())
