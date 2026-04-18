import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_healthcare_data(num_records=10000):
    """
    Generates a synthetic healthcare patient journey dataset locally, 
    bypassing the need for Kaggle API authentication.
    """
    np.random.seed(42)
    random.seed(42)
    
    print(f"Generating {num_records} synthetic healthcare records...")
    
    patient_ids = [f"P{str(i).zfill(5)}" for i in range(1, num_records + 1)]
    
    departments = ['Emergency', 'Cardiology', 'Neurology', 'Radiology', 'Surgery', 'Pediatrics']
    diagnoses = ['HEART FAILURE', 'STROKE', 'PNEUMONIA', 'FRACTURE', 'DIABETES', 'ASTHMA', 'APPENDICITIS']
    
    # Generate Admission Dates over a 6-month period
    start_date = datetime(2023, 7, 1)
    end_date = datetime(2023, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    
    data = []
    for pid in patient_ids:
        # Admission date
        random_number_of_days = random.randrange(days_between_dates)
        random_hour = random.choices(range(24), weights=[1,1,1,1,1,1,2,5,8,9,9,8,7,6,6,5,4,4,5,6,5,4,2,1])[0] # Peak in morning/evening
        random_minute = random.randrange(60)
        
        admit_date = start_date + timedelta(days=random_number_of_days, hours=random_hour, minutes=random_minute)
        
        # Length of stay
        los_days = max(1, int(np.random.gamma(shape=2.0, scale=3.0))) # Skewed distribution for length of stay
        discharge_date = admit_date + timedelta(days=los_days, hours=random.randrange(24))
        
        dept = random.choice(departments)
        diag = random.choice(diagnoses)
        
        # Wait time (depends on dept)
        if dept == 'Emergency':
            wait_time = int(np.random.normal(loc=45, scale=15))
        elif dept == 'Radiology':
            wait_time = int(np.random.normal(loc=30, scale=10))
        else:
            wait_time = int(np.random.normal(loc=15, scale=5))
        
        wait_time = max(0, wait_time)
        
        # Age group mapping (proxy for readmission calculation)
        age = int(np.random.normal(loc=55, scale=20))
        age = max(1, min(100, age))
        
        # Readmission probability (higher for older patients and specific diagnoses)
        readmit_prob = 0.05
        if age > 65: readmit_prob += 0.15
        if diag == 'HEART FAILURE': readmit_prob += 0.10
        readmission = 'YES' if random.random() < readmit_prob else 'NO'
        
        data.append({
            'Patient_ID': pid,
            'Admission_Date': admit_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Discharge_Date': discharge_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Department': dept,
            'Diagnosis': diag,
            'Wait_Time_Minutes': wait_time,
            'Length_of_Stay_Days': los_days,
            'Readmission': readmission,
            'Age': age
        })
        
    df = pd.DataFrame(data)
    
    # Introduce some anomalies for the cleaning script to catch
    # Negative wait times
    df.loc[10:15, 'Wait_Time_Minutes'] = -10
    # Discharge before admit
    df.loc[20:25, 'Discharge_Date'] = (pd.to_datetime(df.loc[20:25, 'Admission_Date']) - timedelta(days=2)).dt.strftime('%Y-%m-%d %H:%M:%S')
    # Missing wait times
    df.loc[30:50, 'Wait_Time_Minutes'] = np.nan
    
    return df

if __name__ == "__main__":
    df = generate_synthetic_healthcare_data()
    # Save to raw
    import os
    os.makedirs('data/raw', exist_ok=True)
    file_path = "data/raw/patient_journey_raw.csv"
    df.to_csv(file_path, index=False)
    print(f"Raw synthetic data saved to {file_path}")