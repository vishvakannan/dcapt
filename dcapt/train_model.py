import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from dcapt.data_processor import load_and_process_data, prepare_features

MODEL_PATH = "dcapt_model.pkl"

def train_model(data_path: str):
    print(f"Loading data from {data_path}...")
    df = load_and_process_data(data_path, is_training=True)
    
    print(f"Loaded {len(df)} rows.")
    
    X, y = prepare_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"MSE: {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    
    # Feature Importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    
    return model

if __name__ == "__main__":
    # Check if dcapt.xlsx exists, otherwise use mock
    if os.path.exists("dcapt.xlsx"):
        train_model("dcapt.xlsx")
    else:
        print("dcapt.xlsx not found. Please provide the data file.")
