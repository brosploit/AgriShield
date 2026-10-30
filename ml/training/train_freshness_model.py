"""AgriShield AI - ML Model Training Pipeline

Generates ground-truth simulated agricultural deterioration telemetry
based on Arrhenius biological degradation curves, and trains a scikit-learn
Random Forest Regressor.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import joblib


def generate_synthetic_agricultural_data(n_samples: int = 2000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)

    # Temperature: 5 to 45 deg C
    temperatures = np.random.uniform(5.0, 45.0, n_samples)
    optimal_temp = 16.0
    temp_dev = temperatures - optimal_temp

    # Humidity: 30% to 98%
    humidities = np.random.uniform(30.0, 98.0, n_samples)
    optimal_hum = 90.0
    hum_dev = humidities - optimal_hum

    # Storage duration: 1 to 240 hours
    storage_hours = np.random.uniform(1.0, 240.0, n_samples)

    # Quantity: 10 to 5000 kg
    quantities = np.random.uniform(10.0, 5000.0, n_samples)

    # Ground truth deterioration risk target (0 - 100)
    # Modeled with thermal acceleration + desiccation/mold stress + time decay
    temp_stress = np.where(temperatures > 20.0, (temperatures - 20.0) * 2.2, 0.0)
    hum_stress = np.where(humidities < 80.0, (80.0 - humidities) * 0.6, (humidities - 92.0) * 0.4)
    time_stress = (storage_hours / 120.0) * 30.0
    noise = np.random.normal(0.0, 3.0, n_samples)

    risk_score = 10.0 + temp_stress + hum_stress + time_stress + noise
    risk_score = np.clip(risk_score, 0.0, 100.0)

    df = pd.DataFrame({
        "temperature_c": temperatures,
        "temp_dev": temp_dev,
        "humidity_pct": humidities,
        "hum_dev": hum_dev,
        "storage_hours": storage_hours,
        "quantity_kg": quantities,
        "risk_score": risk_score,
    })
    return df


def train_and_save_model(output_dir: str = "ml/models"):
    print("Generating simulated agricultural deterioration dataset...")
    df = generate_synthetic_agricultural_data(n_samples=3000)

    # Save dataset
    dataset_dir = Path("ml/datasets")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(dataset_dir / "freshness_training_data.csv", index=False)

    X = df[["temperature_c", "temp_dev", "humidity_pct", "hum_dev", "storage_hours", "quantity_kg"]]
    y = df["risk_score"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"Model Evaluation Metrics:")
    print(f" - MAE: {mae:.2f}")
    print(f" - RMSE: {rmse:.2f}")
    print(f" - R² Score: {r2:.4f}")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    model_file = out_path / "freshness_model.joblib"
    joblib.dump(model, model_file)
    print(f"Model saved successfully to: {model_file}")


if __name__ == "__main__":
    train_and_save_model()

