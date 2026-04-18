import pandas as pd
import json

files = {
    "dept_wait_metrics.csv": "dept_wait_metrics.json",
    "peak_load_heatmap.csv": "peak_load_heatmap.json",
    "readmission_rates.csv": "readmission_rates_by_age.json",  # we'll handle age groups in JS
    "bed_occupancy_daily.csv": "bed_occupancy_daily.json",
    "bed_forecast.csv": "bed_forecast.json",
    "staffing_needs_by_dept_hour.csv": "staffing_needs_by_dept_hour.json"
}

for csv_file, json_file in files.items():
    df = pd.read_csv(f"data/processed/{csv_file}")
    df.to_json(f"data/processed/{json_file}", orient="records", date_format="iso")
    print(f"Converted {csv_file} to {json_file}")