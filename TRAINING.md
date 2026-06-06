# 🎯 Model Training Guide - Indo Bismar AI Forecast

Panduan lengkap untuk melatih dan menggunakan semua model ML dalam sistem.

## Table of Contents
1. [Quick Start Training](#quick-start-training)
2. [Deep Learning Training](#deep-learning-training)
3. [Clustering Training](#clustering-training)
4. [Model Evaluation](#model-evaluation)
5. [Best Practices](#best-practices)

---

## Quick Start Training

### 1. Seed Database dengan Data
```bash
cd backend
python -c "
from seed import seed_sales_from_csv
from database import SessionLocal

db = SessionLocal()
seed_sales_from_csv(db, '../dataset/clean_data_bismar_penjualan.csv', force=False)
print('Database seeded successfully!')
"
```

### 2. Train Traditional ML Model (Product Level)
```bash
cd backend
python train_product_model.py
```

Output:
```
Training on 1500 samples, testing on 300 samples...

[Random Forest]
  -> Training Accuracy: 87.45%
  -> Testing Accuracy : 82.15%

[Gradient Boosting]
  -> Training Accuracy: 89.23%
  -> Testing Accuracy : 84.67%

[Extra Trees]
  -> Training Accuracy: 86.98%
  -> Testing Accuracy : 81.92%

Best model selected: Gradient Boosting (Accuracy: 84.67%)
Saved best model to ./model_product_sales.pkl
```

### 3. Train Deep Learning Models via API
```bash
# Via Python script
python train_deep_learning.py

# Or via API endpoint
curl -X POST "http://localhost:8000/training/train-all"
```

---

## Deep Learning Training

### Training LSTM Model

```python
from deep_learning_models import LSTMForecastModel
from database import SessionLocal
from crud import get_monthly_data_for_forecasting
import numpy as np

# Get data
db = SessionLocal()
monthly_df = get_monthly_data_for_forecasting(db)
monthly_data = monthly_df['kuantitas'].values

# Initialize and train
lstm = LSTMForecastModel(units=64, lookback_window=12)
results = lstm.train(
    data=monthly_data,
    epochs=50,
    batch_size=32,
    validation_split=0.2
)

print(f"LSTM Training Results:")
print(f"  R² Score: {results['train_r2']:.4f}")
print(f"  MAE: {results['train_mae']:.4f}")

# Save model
lstm.save('./backend/models/lstm_model.h5')
```

### Training GRU Model

```python
from deep_learning_models import GRUForecastModel

# Similar to LSTM
gru = GRUForecastModel(units=64, lookback_window=12)
results = gru.train(monthly_data, epochs=50)

print(f"GRU Training Results:")
print(f"  R² Score: {results['train_r2']:.4f}")

gru.save('./backend/models/gru_model.h5')
```

### Making Predictions

```python
# Load models
lstm_model = LSTMForecastModel.load('./backend/models/lstm_model.h5')

# Predict next month
next_month_prediction = lstm_model.predict_next_month(monthly_data)
print(f"LSTM Prediction: {next_month_prediction:.2f}")
```

---

## Clustering Training

### Train Product Clustering

```python
from clustering import ProductClusteringManager
from database import SessionLocal
from crud import get_all_sales_as_dataframe

# Get sales data
db = SessionLocal()
sales_df = get_all_sales_as_dataframe(db)

# Train clustering
clustering = ProductClusteringManager(n_clusters=3)
results = clustering.train(sales_df)

print("Clustering Results:")
print(f"  Total Products: {results['n_products']}")
print(f"  Silhouette Score: {results['silhouette_score']:.4f}")
print(f"  Cluster Sizes: {results['cluster_sizes']}")

# Save model
clustering.save('./backend/models/kmeans_model.pkl')
```

### Get Cluster Summary

```python
# Load clustering model
clustering = ProductClusteringManager.load('./backend/models/kmeans_model.pkl')

# Get summary
summary = clustering.get_cluster_summary()

for cluster in summary:
    print(f"\n{cluster['cluster_name']}:")
    print(f"  Products: {cluster['num_products']}")
    print(f"  Avg Daily Qty: {cluster['avg_daily_qty']:.2f}")
    print(f"  Products: {cluster['products'][:5]}...")  # First 5

# Get specific product cluster
product_cluster = clustering.get_product_cluster("Product A")
print(f"\nProduct A Cluster: {product_cluster['cluster_name']}")
```

---

## Model Evaluation

### Evaluate Ensemble Model

```python
from ml_service import EnsembleMLService
import numpy as np
from sklearn.model_selection import train_test_split

# Prepare data
X = monthly_df[['month_index']].values
y = monthly_df['kuantitas'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train and evaluate
ensemble = EnsembleMLService()
results = ensemble.train_ensemble(X_train, y_train, (X_test, y_test))

print("Ensemble Model Evaluation:")
print(f"  Train R²: {results['train_r2']:.4f}")
print(f"  Test R²: {results.get('test_r2', 'N/A'):.4f}")
print(f"  Train MAE: {results['train_mae']:.4f}")
print(f"  Test MAE: {results.get('test_mae', 'N/A'):.4f}")
```

### Compare All Models

```python
from ml_service import MLPipelineManager

# Load all models
pipeline = MLPipelineManager.load_all_models()

# Get monthly data
monthly_data = get_monthly_data_for_forecasting(db)['kuantitas'].values

# Make predictions
ensemble_pred = None
lstm_pred = None
gru_pred = None

try:
    ensemble_pred = pipeline.predict_ensemble(np.array([[len(monthly_data) + 1]]))
    lstm_pred = pipeline.predict_lstm(monthly_data)
    gru_pred = pipeline.predict_gru(monthly_data)
except Exception as e:
    print(f"Error: {e}")

# Average prediction
valid_preds = [p for p in [ensemble_pred, lstm_pred, gru_pred] if p is not None]
average = np.mean(valid_preds) if valid_preds else 0

print("\nModel Comparison:")
print(f"  Ensemble: {ensemble_pred[0]:.2f}" if ensemble_pred is not None else "  Ensemble: N/A")
print(f"  LSTM: {lstm_pred:.2f}" if lstm_pred is not None else "  LSTM: N/A")
print(f"  GRU: {gru_pred:.2f}" if gru_pred is not None else "  GRU: N/A")
print(f"  Average: {average:.2f}")
print(f"  Best Estimate (Min): {min([p for p in valid_preds if p]):.2f}")
```

---

## Best Practices

### 1. **Data Preparation**
- ✅ Ensure data is clean and complete
- ✅ Handle missing values appropriately
- ✅ Check for outliers
- ✅ Use consistent date formats

### 2. **Model Training**
- ✅ Always use train-test split
- ✅ Use cross-validation for robustness
- ✅ Monitor training/validation loss
- ✅ Save best models to disk
- ✅ Log all training metrics

### 3. **Hyperparameter Tuning**
```python
# Example: Tune LSTM units
for units in [32, 64, 128]:
    lstm = LSTMForecastModel(units=units)
    results = lstm.train(monthly_data, epochs=50)
    print(f"Units: {units}, R²: {results['train_r2']:.4f}")
```

### 4. **Regular Retraining**
- Train models weekly/monthly
- Monitor model drift
- Retrain when accuracy drops
- Keep model version history

### 5. **Production Deployment**
```python
# Load models once on startup
pipeline = MLPipelineManager.load_all_models()

# Use for predictions
def predict_next_month():
    monthly_data = get_monthly_data_for_forecasting(db)['kuantitas'].values
    
    try:
        lstm_pred = pipeline.predict_lstm(monthly_data)
        gru_pred = pipeline.predict_gru(monthly_data)
        
        # Return conservative (lowest) estimate
        return min(lstm_pred, gru_pred)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None
```

### 6. **Monitoring**
- ✅ Track prediction accuracy over time
- ✅ Monitor API response times
- ✅ Log all predictions for audit trail
- ✅ Set up alerts for model failures

---

## Troubleshooting

### Issue: "Not enough data for LSTM"
**Solution:** Need minimum 13 data points (12 months + 1)
```python
# Check data points
if len(monthly_data) < 13:
    print(f"Need 13 data points, have {len(monthly_data)}")
```

### Issue: LSTM training is slow
**Solution:** Reduce `lookback_window` or `epochs`
```python
lstm = LSTMForecastModel(
    units=64,
    lookback_window=6  # Reduced from 12
)
```

### Issue: Low clustering silhouette score
**Solution:** Try different number of clusters
```python
for n_clusters in [2, 3, 4, 5]:
    clustering = ProductClusteringManager(n_clusters=n_clusters)
    results = clustering.train(sales_df)
    print(f"n_clusters={n_clusters}, score={results['silhouette_score']:.4f}")
```

### Issue: Model predictions seem off
**Solution:** Check data quality and retrain
```python
# Verify data
print(f"Data range: {monthly_data.min():.2f} - {monthly_data.max():.2f}")
print(f"Missing values: {np.isnan(monthly_data).sum()}")
print(f"Negative values: {(monthly_data < 0).sum()}")

# Retrain with cleaned data
monthly_data = np.maximum(monthly_data, 0)  # Remove negatives
lstm.train(monthly_data, epochs=100)  # More epochs
```

---

## Performance Tips

### 1. Model Inference Speed
- Use GPU acceleration with TensorFlow
- Batch predictions for multiple items
- Cache model predictions when possible

### 2. Training Speed
- Use smaller `lookback_window` (default 12)
- Reduce `epochs` (start with 50)
- Use smaller `batch_size` for faster iterations
- Use `n_jobs=-1` for ensemble models

### 3. Memory Usage
- Use lower `LSTM_UNITS` (32 instead of 64)
- Reduce `LSTM_EPOCHS` for faster training
- Clear old models from disk

---

## Advanced Topics

### Custom Loss Functions
```python
from tensorflow.keras.losses import MeanSquaredError

# Custom weighted loss
class WeightedMSE(MeanSquaredError):
    def call(self, y_true, y_pred):
        # Penalize underprediction more heavily
        diff = y_true - y_pred
        weighted_diff = tf.where(diff > 0, diff * 1.5, diff)
        return tf.reduce_mean(tf.square(weighted_diff))

# Use in model
model.compile(loss=WeightedMSE(), optimizer='adam')
```

### Ensemble of Deep Learning Models
```python
from tensorflow.keras.layers import Input, Concatenate
from tensorflow.keras.models import Model

# Combine LSTM and GRU
lstm_input = Input(shape=(12, 1))
gru_input = Input(shape=(12, 1))

lstm_out = LSTM(64)(lstm_input)
gru_out = GRU(64)(gru_input)

merged = Concatenate()([lstm_out, gru_out])
output = Dense(1)(merged)

ensemble_model = Model([lstm_input, gru_input], output)
```

---

For more information, see [README.md](README.md)
