import pandas as pd
import numpy as np

def add_time_features(df):
    """Extract hour of day, day of week, and shift categorization from admission time."""
    # Assuming Admission_Date contains time
    df['Admission_Hour'] = df['Admission_Date'].dt.hour
    df['Admission_DayOfWeek'] = df['Admission_Date'].dt.day_name()
    df['Admission_DateOnly'] = df['Admission_Date'].dt.date
    
    # Define shifts (Siemens relevance: aligning staff schedules)
    conditions = [
        (df['Admission_Hour'] >= 7) & (df['Admission_Hour'] < 15),
        (df['Admission_Hour'] >= 15) & (df['Admission_Hour'] < 23),
        (df['Admission_Hour'] >= 23) | (df['Admission_Hour'] < 7)
    ]
    choices = ['Day Shift', 'Evening Shift', 'Night Shift']
    df['Shift'] = np.select(conditions, choices, default='Unknown')
    
    return df

def calculate_department_wait_metrics(df):
    """
    Returns a summary DataFrame of wait time stats by department.
    This will be used for the "Department Throughput" view.
    """
    dept_stats = df.groupby('Department').agg(
        Avg_Wait_Minutes=('Wait_Time_Minutes', 'mean'),
        Median_Wait_Minutes=('Wait_Time_Minutes', 'median'),
        Patient_Volume=('Patient_ID', 'count'),
        Std_Wait_Minutes=('Wait_Time_Minutes', 'std')
    ).reset_index()
    
    # Flag departments with high variability (indicates process inconsistency)
    dept_stats['High_Variability_Flag'] = dept_stats['Std_Wait_Minutes'] > dept_stats['Std_Wait_Minutes'].quantile(0.75)
    return dept_stats

def calculate_peak_load_heatmap(df):
    """
    Creates a pivot table for Power BI heatmap: Rows=Hour, Columns=Day of Week, Values=Patient Count.
    """
    # Ensure we have date column
    df['Date'] = df['Admission_Date'].dt.date
    
    heatmap_data = df.groupby(['Admission_Hour', 'Admission_DayOfWeek']).size().reset_index(name='Patient_Count')
    return heatmap_data

def calculate_readmission_rate_by_diagnosis(df):
    """
    Calculates readmission rate per diagnosis group.
    Formula: (Sum of Readmission flags) / (Total admissions for that diagnosis)
    """
    diag_stats = df.groupby('Diagnosis').agg(
        Total_Admissions=('Patient_ID', 'count'),
        Readmissions=('Readmission', 'sum')
    ).reset_index()
    
    diag_stats['Readmission_Rate'] = (diag_stats['Readmissions'] / diag_stats['Total_Admissions']) * 100
    # Filter out diagnoses with very few cases (noise)
    diag_stats = diag_stats[diag_stats['Total_Admissions'] >= 10]
    return diag_stats

def calculate_bed_occupancy_estimate(df, start_date=None, end_date=None, bed_capacity=100):
    """
    Estimate daily bed occupancy based on length of stay.
    This is a simplified model: For each admission, we generate a 'bed-day' for each day of stay.
    """
    # Remove rows with missing discharge date (assume still inpatient, we'll cap at analysis end date)
    df_valid = df.dropna(subset=['Discharge_Date']).copy()
    
    # Generate a date range for each admission
    all_dates = []
    for _, row in df_valid.iterrows():
        admit = row['Admission_Date'].date()
        discharge = row['Discharge_Date'].date()
        # Create a list of dates the patient occupied a bed (admit day included, discharge day excluded)
        if admit <= discharge:
            dates = pd.date_range(start=admit, end=discharge, freq='D')
            all_dates.extend(dates)
    
    occupancy_series = pd.Series(all_dates).value_counts().sort_index()
    occupancy_df = pd.DataFrame({'Date': occupancy_series.index, 'Occupied_Beds': occupancy_series.values})
    occupancy_df['Occupancy_Rate'] = (occupancy_df['Occupied_Beds'] / bed_capacity) * 100
    
    return occupancy_df

def create_staffing_ratio_indicator(df):
    """
    Create a proxy for staffing ratio: Number of patients per hour of day per department.
    In a real scenario, you'd join with actual staff roster data.
    Here we'll output a file that can be used to simulate understaffing periods.
    """
    load_by_dept_hour = df.groupby(['Department', 'Admission_Hour']).size().reset_index(name='Patient_Count')
    # Assume a simple staffing model: 1 staff per 5 patients is ideal.
    load_by_dept_hour['Recommended_Staff'] = np.ceil(load_by_dept_hour['Patient_Count'] / 5)
    return load_by_dept_hour

def run_feature_engineering(input_path, output_dir):
    """Main feature engineering pipeline."""
    print("Loading cleaned data...")
    df = pd.read_csv(input_path, parse_dates=['Admission_Date', 'Discharge_Date'])
    
    print("Adding time features...")
    df = add_time_features(df)
    
    print("Calculating department wait metrics...")
    dept_wait = calculate_department_wait_metrics(df)
    dept_wait.to_csv(f"{output_dir}/dept_wait_metrics.csv", index=False)
    
    print("Creating peak load heatmap data...")
    heatmap = calculate_peak_load_heatmap(df)
    heatmap.to_csv(f"{output_dir}/peak_load_heatmap.csv", index=False)
    
    print("Calculating readmission rates by diagnosis...")
    readmit = calculate_readmission_rate_by_diagnosis(df)
    readmit.to_csv(f"{output_dir}/readmission_rates.csv", index=False)
    
    print("Estimating bed occupancy...")
    occupancy = calculate_bed_occupancy_estimate(df)
    occupancy.to_csv(f"{output_dir}/bed_occupancy_daily.csv", index=False)
    
    print("Creating staffing ratio indicators...")
    staffing = create_staffing_ratio_indicator(df)
    staffing.to_csv(f"{output_dir}/staffing_needs_by_dept_hour.csv", index=False)
    
    # Also save the fully enriched main dataframe for Power BI
    df.to_csv(f"{output_dir}/patient_journey_enriched.csv", index=False)
    print(f"All feature files saved to {output_dir}")
    
    return df

if __name__ == "__main__":
    run_feature_engineering(
        "data/processed/patient_journey_cleaned.csv",
        "data/processed/"
    )