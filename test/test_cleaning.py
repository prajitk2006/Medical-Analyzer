import pytest
import pandas as pd
from src.data_cleaning import parse_dates, flag_anomalies, clean_categoricals

def test_parse_dates():
    df = pd.DataFrame({'Admission_Date': ['2023-01-01', 'invalid'], 'Discharge_Date': ['2023-01-02', '2023-01-03']})
    result = parse_dates(df)
    assert pd.isna(result.loc[1, 'Admission_Date'])
    assert result.loc[0, 'Admission_Date'].year == 2023

def test_flag_anomalies_negative_wait():
    df = pd.DataFrame({
        'Admission_Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'Discharge_Date': pd.to_datetime(['2023-01-02', '2023-01-01']), # second row: discharge before admit
        'Wait_Time_Minutes': [1440, -100],
        'Length_of_Stay_Days': [1, 1]
    })
    result = flag_anomalies(df)
    assert result.loc[1, 'flag_discharge_before_admit'] == True
    assert result.loc[1, 'flag_negative_wait'] == True

def test_clean_categoricals_readmission_map():
    df = pd.DataFrame({'Readmission': ['Yes', 'No', 'YES'], 'Department': ['ER', 'icu', 'Radiology'], 'Diagnosis': ['Flu', 'Covid', 'Fracture']})
    result = clean_categoricals(df)
    assert result.loc[0, 'Readmission'] == 1
    assert result.loc[1, 'Readmission'] == 0
    assert result.loc[1, 'Department'] == 'Icu'
    assert result.loc[2, 'Diagnosis'] == 'FRACTURE'