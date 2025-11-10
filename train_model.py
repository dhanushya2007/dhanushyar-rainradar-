"""
ML Model Training Script for Rainfall Prediction
Trains a Random Forest Regressor on historical weather data
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os

def train_model():
    """Train the rainfall prediction model"""
    
    # Load dataset
    data_path = 'data/weather_data.csv'
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print("Please ensure weather_data.csv exists in the data/ directory")
        return
    
    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Display dataset info
    print(f"\nDataset shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nDataset info:")
    print(df.info())
    print(f"\nDataset statistics:")
    print(df.describe())
    
    # Feature selection
    features = ['temperature', 'humidity', 'wind_speed', 'pressure', 'past_rainfall']
    target = 'rainfall'
    
    # Check if all required columns exist
    missing_cols = [col for col in features + [target] if col not in df.columns]
    if missing_cols:
        print(f"\nError: Missing columns: {missing_cols}")
        return
    
    X = df[features]
    y = df[target]
    
    # Handle missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    # Split data
    print("\nSplitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("\nTraining Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Evaluate model
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("\n" + "="*50)
    print("Model Evaluation Metrics:")
    print("="*50)
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"R² Score: {r2:.4f}")
    print("="*50)
    
    # Feature importance
    print("\nFeature Importance:")
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance)
    
    # Save model
    model_dir = 'model'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    model_path = os.path.join(model_dir, 'rainfall_model.joblib')
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save feature names for later use
    feature_path = os.path.join(model_dir, 'feature_names.joblib')
    joblib.dump(features, feature_path)
    print(f"Feature names saved to: {feature_path}")
    
    print("\nTraining completed successfully!")

if __name__ == '__main__':
    train_model()

