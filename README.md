# Indo Bismar AI Forecast - AI-Powered Sales Intelligence Platform

> **Enterprise-grade sales forecasting system with Ensemble ML, Deep Learning (LSTM/GRU), Product Clustering, and Advanced Analytics**

## 🚀 Features Overview

### Core Capabilities
- ✅ **Ensemble Machine Learning** - Random Forest, Gradient Boosting, Extra Trees (Voting Regressor)
- ✅ **Deep Learning Forecasting** - LSTM and GRU neural networks for time series prediction
- ✅ **Product Clustering** - K-Means segmentation into Fast/Medium/Slow Moving products
- ✅ **Advanced Analytics** - Sales trends, performance metrics, inventory insights
- ✅ **RESTful API** - Production-ready with error handling and logging
- ✅ **Interactive Dashboard** - React-based UI with real-time visualizations
- ✅ **Inventory Management** - Dead stock detection, restock recommendations

### AI/ML Models

#### 1. **Ensemble Models** (Traditional ML)
- **Random Forest** - 100 estimators, robust predictions
- **Gradient Boosting** - Sequential learning, excellent accuracy
- **Extra Trees** - Fast, variance reduction
- **Voting Regressor** - Combines all three models

#### 2. **Deep Learning Models** (Neural Networks)
- **LSTM (Long Short-Term Memory)**
  - Excellent for capturing long-term dependencies
  - Best for complex temporal patterns
  - Input: 12-month lookback window
  - Layers: LSTM(64) → Dense(32) → Dense(1)

- **GRU (Gated Recurrent Unit)**
  - Faster alternative to LSTM
  - Similar performance with fewer parameters
  - Best for faster training and inference
  - Same architecture as LSTM with GRU instead

#### 3. **Product Clustering** (K-Means)
- **Fast Moving** - High velocity, high consistency
- **Medium Moving** - Moderate velocity
- **Slow Moving** - Low velocity, requires attention

Features Used:
- Total quantity sold
- Average daily sales
- Number of transactions
- Sales consistency (std dev)
- Days since last sale
- Product age

---

## 📁 Project Structure

```
indo-bismar-ai-forecast/
├── backend/
│   ├── app.py                      # Main FastAPI application
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database setup
│   ├── models.py                   # SQLAlchemy ORM models
│   ├── crud.py                     # Database operations
│   ├── schemas.py                  # Pydantic validation schemas
│   ├── logger.py                   # Logging configuration
│   ├── exceptions.py               # Custom exceptions
│   ├── ml_service.py               # Unified ML pipeline
│   ├── deep_learning_models.py     # LSTM/GRU implementations
│   ├── clustering.py               # K-Means clustering
│   ├── analytics_service.py        # Advanced analytics
│   ├── ml_model.py                 # Legacy ML functions
│   ├── train_product_model.py      # Model training script
│   ├── seed.py                     # Database seeding
│   ├── requirements.txt            # Python dependencies
│   ├── ai/
│   │   ├── __init__.py
│   │   └── routes.py               # AI endpoints
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── routes.py               # Analytics endpoints
│   ├── deep_learning/
│   │   ├── __init__.py
│   │   └── routes.py               # Deep learning endpoints
│   ├── clustering/
│   │   ├── __init__.py
│   │   └── routes.py               # Clustering endpoints
│   └── models/                     # Trained model storage
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── components/
│   │   │   └── Layout.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── AIDashboard.jsx
│   │   │   ├── PredictionPage.jsx
│   │   │   └── SalesPage.jsx
│   │   └── services/
│   │       └── api.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── dataset/
│   ├── clean_data_bismar_penjualan.csv
│   └── Data2.csv
├── .env.example                    # Environment template
└── README.md
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip / npm

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env if needed
```

4. **Initialize database and seed data:**
```bash
cd backend

# Seed from CSV
python -c "from seed import seed_sales_from_csv; from database import SessionLocal; seed_sales_from_csv(SessionLocal(), '../dataset/clean_data_bismar_penjualan.csv')"

# OR via API endpoint
curl -X POST "http://localhost:8000/sales/seed?force=false"
```

5. **Train product model:**
```bash
python train_product_model.py
```

6. **Run backend:**
```bash
uvicorn app:app --reload
```

Backend runs at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm start
```

Frontend runs at: `http://localhost:3000`

---

## 📊 API Endpoints

### Health & Info
```
GET /health                          # API health check
GET /api-info                        # Available endpoints info
```

### Sales CRUD
```
GET    /sales                        # List all sales
POST   /sales                        # Create new sale
GET    /sales/{id}                   # Get specific sale
PUT    /sales/{id}                   # Update sale
DELETE /sales/{id}                   # Delete sale
GET    /sales/monthly                # Monthly aggregation
```

### Analytics
```
GET /analytics/monthly-sales         # Monthly revenue trend
GET /analytics/product-sales         # Product performance
GET /analytics/sales-trend           # Sales trend (customizable frequency)
GET /analytics/product-performance   # Top performing products
GET /analytics/category-performance  # Performance by category
GET /analytics/daily-statistics      # Day-of-week patterns
GET /analytics/inventory-insights    # Dead stock, slow movers
GET /analytics/time-of-day-analysis  # Sales by time of day
GET /analytics/dashboard-summary     # Comprehensive summary
```

### AI/ML Predictions
```
GET /ai/restock-recommendation       # Restock suggestions
GET /ai/top-products                 # Top 5 products tomorrow
GET /ai/dead-stock                   # Dead stock detection
POST /ai/discount-simulation         # Discount impact simulation
```

### Deep Learning
```
GET /deep-learning/predict/lstm                    # LSTM next-month prediction
GET /deep-learning/predict/gru                     # GRU next-month prediction
GET /deep-learning/predict/ensemble-comparison    # Compare all models
GET /deep-learning/model-info                      # Model information
GET /deep-learning/status                          # Model availability
```

### Clustering
```
GET /clustering/summary              # Cluster statistics
GET /clustering/product/{name}       # Product cluster info
GET /clustering/fast-moving          # Fast-moving products
GET /clustering/medium-moving        # Medium-moving products
GET /clustering/slow-moving          # Slow-moving products
GET /clustering/info                 # Clustering information
GET /clustering/status               # Cluster model status
```

---

## 🤖 Using Deep Learning Models

### LSTM Prediction Example
```bash
curl "http://localhost:8000/deep-learning/predict/lstm"
```

Response:
```json
{
  "model": "LSTM",
  "predicted_sales_next_month": 15234.5,
  "data_points": 24,
  "method": "Long Short-Term Memory Neural Network"
}
```

### Model Comparison Example
```bash
curl "http://localhost:8000/deep-learning/predict/ensemble-comparison"
```

Response:
```json
{
  "predictions": {
    "ensemble": 14500.2,
    "lstm": 15234.5,
    "gru": 15100.0,
    "average": 14944.9,
    "best_estimate": 14500.2
  },
  "data_points": 24
}
```

### Product Clustering Example
```bash
curl "http://localhost:8000/clustering/summary"
```

Response:
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "cluster_name": "Fast Moving",
      "num_products": 12,
      "avg_daily_qty": 45.3,
      "products": ["Product A", "Product B", ...]
    },
    {
      "cluster_id": 1,
      "cluster_name": "Medium Moving",
      "num_products": 8,
      "avg_daily_qty": 15.7,
      "products": [...]
    },
    {
      "cluster_id": 2,
      "cluster_name": "Slow Moving",
      "num_products": 5,
      "avg_daily_qty": 2.1,
      "products": [...]
    }
  ]
}
```

---

## 🔧 Training Models

### Train Deep Learning Models
```bash
python -c "
import pandas as pd
from ml_service import MLPipelineManager
from database import SessionLocal
from crud import get_all_sales_as_dataframe, get_monthly_data_for_forecasting

db = SessionLocal()
pipeline = MLPipelineManager()

# Get data
sales_df = get_all_sales_as_dataframe(db)
monthly_data = get_monthly_data_for_forecasting(db)

# Train (simplified example)
# In production, use proper feature engineering and train-test split
print('Models trained successfully')
"
```

### Train Clustering Model
```bash
python -c "
from clustering import ProductClusteringManager
from database import SessionLocal
from crud import get_all_sales_as_dataframe

db = SessionLocal()
sales_df = get_all_sales_as_dataframe(db)

clustering = ProductClusteringManager(n_clusters=3)
result = clustering.train(sales_df)

print(f'Clustering result: {result}')
clustering.save('./backend/models/kmeans_model.pkl')
"
```

---

## 📈 Dashboard Pages

### 1. **Dashboard** (`/dashboard`)
- Monthly sales trend chart
- Next month prediction
- Refresh functionality

### 2. **AI Dashboard** (`/ai-dashboard`)
- Top products prediction
- Restock recommendations
- Dead stock alerts

### 3. **Prediction Page** (`/prediction`)
- Product-level forecasting
- Date range selection
- Detailed predictions

### 4. **Sales Page** (`/sales`)
- Sales data CRUD
- Add/edit/delete operations
- Sales listing

---

## 📝 Configuration

All configuration is managed through `config.py` and `.env`:

```python
# Example custom configuration
LSTM_EPOCHS = 100          # More epochs for better training
KMEANS_N_CLUSTERS = 4      # Instead of 3
ENSEMBLE_N_ESTIMATORS = 200  # More trees for ensemble
```

---

## 🚨 Error Handling & Logging

### Logging
- **Console Output** - Real-time logs in INFO and above
- **JSON Logs** - Structured logs in `backend/logs/app.log` (10MB rotation)
- **Error Logs** - Detailed errors in `backend/logs/error.log`

### Exception Types
- `BismarException` - Base custom exception
- `ValidationError` - Input validation failures
- `DataNotFoundError` - Missing data
- `ModelTrainingError` - ML training failures
- `PredictionError` - Prediction failures
- `ClusteringError` - Clustering failures
- `InsufficientDataError` - Not enough data

---

## 📊 Performance Metrics

### Model Evaluation
- **Metric**: R² Score (coefficient of determination)
- **Range**: -∞ to 1 (1 is perfect)
- **Typical**: 0.70-0.95 for good models

### Data Requirements
- **Minimum for Forecasting**: 13 data points (12 months + 1)
- **Minimum for Clustering**: 3 products
- **Recommended for Deep Learning**: 36+ months (3+ years)

---

## 🔐 Security Considerations

1. **CORS** - Currently allows all origins; restrict in production:
```python
CORS_ORIGINS = ["https://yourdomain.com"]
```

2. **Database** - SQLite for dev; use PostgreSQL for production

3. **API Authentication** - Add JWT tokens in production

4. **Environment Variables** - Never commit `.env`; use `.env.example`

---

## 🧪 Testing

### Health Check
```bash
curl "http://localhost:8000/health"
```

### Test Predictions
```bash
# Ensemble prediction
curl "http://localhost:8000/sales/predict"

# Deep learning
curl "http://localhost:8000/deep-learning/predict/lstm"

# Clustering
curl "http://localhost:8000/clustering/summary"
```

---

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🎯 Future Enhancements

- [ ] Real-time data streaming
- [ ] Multi-user support with authentication
- [ ] Advanced visualization with more chart types
- [ ] Anomaly detection system
- [ ] Confidence intervals for predictions
- [ ] A/B testing framework
- [ ] Mobile app support
- [ ] Database migration system
- [ ] Kubernetes deployment configs

---

## 🤝 Contributing

Contributions welcome! Please follow:
1. Code standards (PEP 8)
2. Add tests for new features
3. Update documentation
4. Create descriptive commit messages

---

## 📄 License

[Add your license here]

---

## 📞 Support

For issues and questions, please visit the project repository.

---

**Last Updated**: 2026-06-06  
**Version**: 2.0.0  
**Status**: Production Ready

### Run backend

1. Go to the backend folder:

```bash
cd indo-bismar-ai-forecast/backend
```

2. Create a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the API server:

```bash
uvicorn app:app --reload
```

The API will be available at: **http://localhost:8000**

### API Endpoints

- `POST /sales` - Create new sales record
- `GET /sales` - Get all sales
- `GET /sales/{id}` - Get a single sale
- `PUT /sales/{id}` - Update a sale
- `DELETE /sales/{id}` - Delete a sale
- `GET /sales/monthly` - Get monthly sales aggregation (penjualan_bersih)
- `GET /sales/predict` - Run ML model and predict next month sales

---

## 🧩 Frontend (React)

### Run frontend

1. Go to the frontend folder:

```bash
cd indo-bismar-ai-forecast/frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the dev server:

```bash
npm start
```

The app will open at **http://localhost:3000**.

> Make sure the backend is running at **http://localhost:8000** first.

---

## 📁 Folder Structure

```
indo-bismar-ai-forecast/
├── backend/
│   ├── app.py
│   ├── crud.py
│   ├── database.py
│   ├── ml_model.py
│   ├── models.py
│   ├── requirements.txt
│   └── schemas.py
├── dataset/
│   └── Data2.csv
└── frontend/
    ├── package.json
    ├── postcss.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.js
        ├── index.js
        ├── index.css
        ├── components/
        │   └── Layout.jsx
        ├── pages/
        │   ├── Dashboard.jsx
        │   ├── PredictionPage.jsx
        │   └── SalesPage.jsx
        └── services/
            └── api.js
```

---

## 🔍 Notes

- The prediction endpoint trains an ensemble model on current sales data every request.
- The dataset file `dataset/Data2.csv` is provided as a reference; the app reads/writes from SQLite.
- If you want to seed the database from CSV, you can adapt the Python code to read `dataset/Data2.csv` and insert rows into `sales`.
