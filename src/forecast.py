import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta

def create_forecast(input_file, output_file, days_to_forecast=7):
    """
    Train a simple linear regression model to predict bed occupancy 
    for the next 'days_to_forecast' days.
    """
    print("Loading historical bed occupancy data...")
    df = pd.read_csv(input_file)
    
    # Ensure Date is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Feature engineering for simple regression: Days since start
    df['Days_Since_Start'] = (df['Date'] - df['Date'].min()).dt.days
    
    # Prepare X and y
    X = df[['Days_Since_Start']]
    y = df['Occupied_Beds']
    
    # Train Linear Regression model
    print("Training Simple Linear Regression model for forecast...")
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates
    last_date = df['Date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_to_forecast + 1)]
    future_days_since_start = [(d - df['Date'].min()).days for d in future_dates]
    
    # Predict
    X_future = pd.DataFrame({'Days_Since_Start': future_days_since_start})
    predictions = model.predict(X_future)
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Forecasted_Beds': np.round(predictions).astype(int)
    })
    
    # Save to CSV
    forecast_df.to_csv(output_file, index=False)
    print(f"Forecast saved to {output_file}")
    return forecast_df

if __name__ == "__main__":
    create_forecast(
        input_file="data/processed/bed_occupancy_daily.csv",
        output_file="data/processed/bed_forecast.csv"
    )
