import pandas as pd
import os

def load_data(data_dir):
    """
    Loads all relevant CSV files from the specified directory.
    """
    files = {
        'patients': 'patients.csv',
        'encounters': 'encounters.csv',
        'conditions': 'conditions.csv',
        'observations': 'observations.csv',
        'careplans': 'careplans.csv',
        'allergies': 'allergies.csv',
        'immunizations': 'immunizations.csv'
    }
    
    datasets = {}
    for name, filename in files.items():
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            datasets[name] = pd.read_csv(path)
            print(f"Loaded {name}: {datasets[name].shape}")
        else:
            print(f"Warning: {filename} not found in {data_dir}")
            
    return datasets

def clean_data(datasets):
    """
    Basic cleaning: date conversion and missing value handling.
    """
    # Standardize column names to be consistent (some might be Id, some PATIENT)
    # Synthea usually uses 'Id' in patients.csv and 'PATIENT' in others.
    
    if 'patients' in datasets:
        datasets['patients']['BIRTHDATE'] = pd.to_datetime(datasets['patients']['BIRTHDATE'])
        if 'DEATHDATE' in datasets['patients'].columns:
            datasets['patients']['DEATHDATE'] = pd.to_datetime(datasets['patients']['DEATHDATE'])
            
    # Convert other date columns
    date_cols = {
        'encounters': ['START', 'STOP'],
        'conditions': ['START', 'STOP'],
        'observations': ['DATE'],
        'careplans': ['START', 'STOP'],
        'allergies': ['START', 'STOP'],
        'immunizations': ['DATE']
    }
    
    for df_name, cols in date_cols.items():
        if df_name in datasets:
            for col in cols:
                if col in datasets[df_name].columns:
                    datasets[df_name][col] = pd.to_datetime(datasets[df_name][col])
                    
    return datasets

if __name__ == "__main__":
    DATA_DIR = "/Users/rajendran/Desktop/cdss/data"
    data = load_data(DATA_DIR)
    data = clean_data(data)
    print("Pre-processing complete.")
