import pytest
import pandas as pd
from src.feature_engineering import add_time_features, calculate_readmission_rate_by_diagnosis

def test_add_time_features_shift():
    df = pd.DataFrame({'Admission_Date': pd.to_datetime(['2023-01-01 08:00:00', '2023-01-01 20:00:00', '2023-01-01 01:00:00'])})
    result = add_time_features(df)
    assert result.loc[0, 'Shift'] == 'Day Shift'
    assert result.loc[1, 'Shift'] == 'Evening Shift'
    assert result.loc[2, 'Shift'] == 'Night Shift'

def test_readmission_rate_calculation():
    df = pd.DataFrame({
        'Patient_ID': list(range(1, 21)),
        'Diagnosis': ['FLU']*10 + ['COVID']*10,
        'Readmission': [1]*5 + [0]*5 + [1]*10 # 50% for FLU, 100% for COVID
    })
    result = calculate_readmission_rate_by_diagnosis(df)
    flu_row = result[result['Diagnosis'] == 'FLU']
    covid_row = result[result['Diagnosis'] == 'COVID']
    assert flu_row['Readmission_Rate'].values[0] == 50.0
    assert covid_row['Readmission_Rate'].values[0] == 100.0