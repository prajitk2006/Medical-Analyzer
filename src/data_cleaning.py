import pandas as pd
import numpy as np
from datetime import datetime

def load_raw_data(filepath):
    """Load raw CSV data."""
    return pd.read_csv(filepath)

def parse_dates(df):
    """Convert object columns to datetime. Handle errors by coercing to NaT."""
    date_cols = ['Admission_Date', 'Discharge_Date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def flag_anomalies(df):
    """
    Create boolean flags for data quality issues.
    - Negative wait times
    - Discharge before admission
    - Future dates
    - Extreme length of stay (> 365 days)
    """
    # Wait time column already exists in dataset, but we recalc to check integrity
    df['calc_wait_time'] = (df['Discharge_Date'] - df['Admission_Date']).dt.total_seconds() / 60
    
    df['flag_negative_wait'] = df['Wait_Time_Minutes'] < 0
    df['flag_discharge_before_admit'] = df['Discharge_Date'] < df['Admission_Date']
    df['flag_future_admit'] = df['Admission_Date'] > datetime.now()
    df['flag_extreme_los'] = df['Length_of_Stay_Days'] > 365
    
    # Flag where calculated wait time doesn't match provided wait time (significant diff > 5 mins)
    df['flag_wait_mismatch'] = (df['Wait_Time_Minutes'] - df['calc_wait_time']).abs() > 5
    
    return df

def handle_missing_values(df):
    """
    Documented strategy for missing data.
    - Patient_ID: Drop rows without ID (can't track patient journey).
    - Discharge_Date: If missing, patient likely still inpatient. We'll create a separate 'Discharge_Status' column later.
    - Wait_Time_Minutes: Impute with median per department if missing, but flag.
    """
    initial_len = len(df)
    df = df.dropna(subset=['Patient_ID']).copy()
    print(f"Dropped {initial_len - len(df)} rows due to missing Patient_ID.")
    
    # For discharge date, we'll keep NaT and handle in feature engineering
    # For wait time, we'll impute with median by department but flag
    df['flag_imputed_wait'] = df['Wait_Time_Minutes'].isna()
    df['Wait_Time_Minutes'] = df.groupby('Department')['Wait_Time_Minutes'].transform(
        lambda x: x.fillna(x.median())
    )
    
    return df

def clean_categoricals(df):
    """Standardize text columns."""
    df['Department'] = df['Department'].str.strip().str.title()
    df['Diagnosis'] = df['Diagnosis'].str.strip().str.upper()
    df['Readmission'] = df['Readmission'].astype(str).str.upper().map({'YES': 1, 'NO': 0})
    return df

def run_cleaning_pipeline(input_path, output_path):
    """Main ETL function."""
    print("Loading raw data...")
    df = load_raw_data(input_path)
    
    print("Parsing dates...")
    df = parse_dates(df)
    
    print("Flagging anomalies...")
    df = flag_anomalies(df)
    
    print("Handling missing values...")
    df = handle_missing_values(df)
    
    print("Standardizing categories...")
    df = clean_categoricals(df)
    
    # Save cleaned data
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")
    return df

if __name__ == "__main__":
    run_cleaning_pipeline("data/raw/patient_journey_raw.csv", "data/processed/patient_journey_cleaned.csv")