# AgriShield AI — Machine Learning & Agronomic Science Model

The AgriShield AI Freshness Intelligence engine predicts produce deterioration and remaining shelf life by unifying **biochemical respiration kinetics** with a **Scikit-learn Random Forest regression model**.

---

## 1. Mathematical Formulations

### 1.1 Respiration Thermal Acceleration ($Q_{10}$ Law)
Post-harvest crops continue cellular respiration, consuming sugars and releasing heat, moisture, and carbon dioxide. Biological deterioration accelerates exponentially with temperature deviations above the crop-specific optimal storage envelope:

$$Q_{10} = 2.0^{\frac{T - T_{\text{optimal}}}{10}}$$

Where:
- $T$: Current ambient storage temperature (°C).
- $T_{\text{optimal}}$: The midpoint of the crop's physiological optimal storage temperature range.
- Base coefficient: $2.0$ represents the biological doubling of metabolic enzyme activity per 10°C thermal increase (calibrated to $2.2$ for high-respiration perishables like tomatoes, $2.5$ for mangoes, and $1.5$ for durable grains).

### 1.2 Vapor Pressure Deficit (VPD) Stress
Transpiration and biological moisture loss are governed by the gradient between saturated internal vapor pressure and ambient atmospheric vapor pressure:

$$e_s(T) = 0.6108 \cdot \exp\left(\frac{17.27 \cdot T}{T + 237.3}\right) \quad [\text{kPa}]$$

$$e_a = e_s(T) \cdot \left(\frac{\text{RH}}{100}\right) \quad [\text{kPa}]$$

$$\text{VPD} = \max(0, e_s(T) - e_a) \quad [\text{kPa}]$$

When $\text{VPD} > 1.2\text{ kPa}$, desiccation stress intensifies, applying a non-linear degradation penalty:
$$\text{Penalty}_{\text{VPD}} = \max(0, \text{VPD} - 1.2) \cdot 12.0$$

### 1.3 Effective Biological Elapsed Hours
Storage environments either mitigate or amplify deterioration:
$$\text{Hours}_{\text{effective}} = \text{Hours}_{\text{elapsed}} \cdot Q_{10} \cdot M_{\text{storage}} \cdot M_{\text{transport}}$$

Where $M_{\text{storage}}$ values are calibrated as:
- Open Air / Sun: $1.40\times$
- Traditional Ambient Shed: $1.15\times$
- Ventilated Godown: $0.85\times$
- Hermetic Silo: $0.40\times$
- Cold Storage / Chilled: $0.25\times$

---

## 2. Machine Learning Training Pipeline

The ML pipeline is located in `ml/training/train_freshness_model.py`.

```mermaid
flowchart LR
    Dataset["Synthetic Agronomic\nDataset (10,000 rows)"] --> Prep["Feature Extraction\n& One-Hot Encoding"]
    Prep --> Split["80/20 Train-Test\nStratified Split"]
    Split --> RF["Random Forest Regressor\n(n_estimators=100)"]
    RF --> Eval["Evaluation & Metrics\n(MAE, RMSE, R²)"]
    Eval --> Persist["Joblib Serialization\n(ml/models/freshness_model.joblib)"]
```

### 2.1 Model Architecture & Hyperparameters
- **Estimator:** `sklearn.ensemble.RandomForestRegressor`
- **Number of Trees:** `100`
- **Max Depth:** `16`
- **Min Samples Split:** `4`
- **Random State:** `42`

### 2.2 Model Verification Metrics
Evaluated on holdout agricultural test telemetry:

| Metric | Holdout Evaluation Score |
| :--- | :--- |
| **Coefficient of Determination ($R^2$)** | **0.9797** (~0.98) |
| **Mean Absolute Error (MAE)** | **2.77** risk points |
| **Root Mean Squared Error (RMSE)** | **3.63** risk points |

---

## 3. Retraining Instructions

To retrain and update the production model artifact:
```bash
# Execute training script
python ml/training/train_freshness_model.py

# Evaluate cross-validation
python ml/evaluation/evaluate_model.py
```
The script will regenerate `ml/datasets/freshness_training_data.csv` and compile the fresh binary to `ml/models/freshness_model.joblib`.

