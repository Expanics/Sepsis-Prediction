import joblib
import pandas as pd
import numpy as np
import os
import sklearn

print(f"Sklearn version: {sklearn.__version__}")

model_dir = "../model"
scaler_path = os.path.join(model_dir, "scaler_X.joblib")

try:
    scaler = joblib.load(scaler_path)
    print("Scaler loaded.")
    
    if hasattr(scaler, "feature_names_in_"):
        print("Feature names found:")
        print(scaler.feature_names_in_)
        print(f"Count: {len(scaler.feature_names_in_)}")
    else:
        print("No feature_names_in_ found.")
        print(f"n_features_in_: {scaler.n_features_in_}")
        
    if hasattr(scaler, "mean_"):
        print(f"Mean shape: {scaler.mean_.shape}")
        
except Exception as e:
    print(f"Error: {e}")
