# 🏗️ System Architecture - Indo Bismar AI Forecast

Dokumentasi lengkap arsitektur sistem, komponen, dan alur data.

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Clean Architecture Pattern](#clean-architecture-pattern)
6. [Deployment Architecture](#deployment-architecture)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
├─────────────────────────────────────────────────────────────┤
│  React Dashboard  │  Mobile App  │  Third-party Systems   │
└────────────────────────┬──────────────────────────────────┘
                         │ HTTPS/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway Layer                          │
├─────────────────────────────────────────────────────────────┤
│  FastAPI  │  CORS  │  Error Handler  │  Logger             │
└────────────┬───────────────────────────────────────────────┘
             │
┌────────────┴────────────────────────────────────────────────┐
│                  Application Layer                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Sales Routes │  │ AI Routes    │  │ Analytics    │      │
│  │ (CRUD)       │  │ (Prediction) │  │ Routes       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────┴──────────────────┴──────────────────┴────┐        │
│  │           Service Layer                        │        │
│  │                                                │        │
│  │  ┌──────────────┐  ┌──────────────────┐      │        │
│  │  │ ML Service   │  │ Analytics        │      │        │
│  │  │ Pipeline     │  │ Service          │      │        │
│  │  └──────┬───────┘  └──────────────────┘      │        │
│  └─────────┼────────────────────────────────────┘        │
│            │                                             │
│  ┌─────────┴─────────────────────────────────┐          │
│  │        ML/Data Layer                       │          │
│  │                                            │          │
│  │  ┌───────────────┐  ┌─────────────────┐   │          │
│  │  │ Ensemble      │  │ Deep Learning   │   │          │
│  │  │ (RF,GB,ET)    │  │ (LSTM/GRU)      │   │          │
│  │  └───────────────┘  └─────────────────┘   │          │
│  │                                            │          │
│  │  ┌─────────────────────────────────┐      │          │
│  │  │ Clustering (K-Means)            │      │          │
│  │  └─────────────────────────────────┘      │          │
│  └────────────┬─────────────────────────────┘          │
└───────────────┼────────────────────────────────────────┘
                │
┌───────────────┴────────────────────────────────────────┐
│              Data Layer                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐              ┌─────────────────┐    │
│  │   SQLite     │              │  Trained Models │    │
│  │   Database   │              │  (h5, pkl)      │    │
│  └──────────────┘              └─────────────────┘    │
│                                                         │
│  ┌──────────────┐              ┌─────────────────┐    │
│  │   CSV Files  │              │   Logs          │    │
│  │   (Dataset)  │              │   (JSON)        │    │
│  └──────────────┘              └─────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. **Frontend (Client Layer)**
- **React Application**
  - Components: Layout, Pages (Dashboard, Predictions, Sales)
  - Services: API Client (axios)
  - Styling: Tailwind CSS
  - Charts: Recharts
  - State Management: React Hooks

### 2. **API Gateway (FastAPI)**
- **Main Application** (`app.py`)
  - CORS Middleware
  - Error Handlers
  - Route Registration
  - Health Checks

### 3. **Routes Layer**
#### Sales Routes
- CRUD operations
- Monthly aggregations
- Seed from CSV

#### AI Routes
- Restock recommendations
- Top products
- Dead stock detection
- Discount simulation

#### Analytics Routes
- Sales trends
- Product performance
- Category analysis
- Inventory insights
- Time analysis
- Dashboard summary

#### Deep Learning Routes
- LSTM predictions
- GRU predictions
- Model comparison
- Model information

#### Clustering Routes
- Cluster summary
- Product classification
- Fast/Medium/Slow moving products

### 4. **Service Layer**

#### ML Service (`ml_service.py`)
```python
MLPipelineManager
├── EnsembleMLService
│   └── VotingRegressor (RF + GB + ET)
├── LSTMForecastModel
│   └── LSTM Neural Network
├── GRUForecastModel
│   └── GRU Neural Network
└── ProductClusteringManager
    └── K-Means Clustering
```

#### Analytics Service (`analytics_service.py`)
```python
SalesAnalyticsService
├── get_sales_trend()
├── get_product_performance()
├── get_category_performance()
├── get_daily_statistics()
├── get_inventory_insights()
└── get_time_of_day_analysis()
```

### 5. **Data Layer**

#### Models (`models.py`)
```python
Sales (SQLAlchemy ORM)
├── id (Primary Key)
├── tanggal (DateTime)
├── nama_barang (Product Name)
├── kategori (Category)
├── kuantitas (Quantity)
├── day_type (Weekday/Weekend)
├── waktu (Time Slot)
└── ... (other fields)
```

#### CRUD Operations (`crud.py`)
- Sales CRUD
- Product operations
- Monthly aggregations
- Advanced queries

#### Database (`database.py`)
- SQLite connection
- Session management
- ORM setup

### 6. **ML/Data Components**

#### Ensemble ML (`ml_model.py`, `ml_service.py`)
- Random Forest (100 estimators)
- Gradient Boosting (100 estimators)
- Extra Trees (100 estimators)
- Voting Regressor (ensemble)

#### Deep Learning (`deep_learning_models.py`)
- LSTM Model
  - Input: 12-month window
  - Hidden: 64 units
  - Layers: LSTM → Dense(32) → Dense(1)
  - Activation: relu

- GRU Model
  - Similar architecture to LSTM
  - Faster training/inference

#### Clustering (`clustering.py`)
- K-Means (3 clusters)
- Features:
  - total_qty
  - avg_daily_qty
  - num_transactions
  - sales_std
  - days_since_last
  - product_age

---

## Data Flow

### 1. **Sales Data Entry Flow**
```
User Input (Frontend)
    ↓
POST /sales (API)
    ↓
create_sales() (CRUD)
    ↓
Validate & Transform
    ↓
Insert into SQLite
    ↓
Refresh & Return
    ↓
Display in Frontend
```

### 2. **Prediction Flow**
```
GET /sales/predict
    ↓
get_monthly_data() (CRUD)
    ↓
Load Sales from Database
    ↓
Aggregate by Month
    ↓
Train Ensemble Model (on-the-fly)
    ↓
Make Prediction
    ↓
Return Result
```

### 3. **Deep Learning Flow**
```
GET /deep-learning/predict/lstm
    ↓
Load LSTM Model (cached from startup)
    ↓
Get Monthly Data
    ↓
Normalize Data (MinMaxScaler)
    ↓
Use Lookback Window (12 months)
    ↓
Neural Network Inference
    ↓
Denormalize Prediction
    ↓
Return Result
```

### 4. **Clustering Flow**
```
GET /clustering/summary
    ↓
Load Clustering Model (cached)
    ↓
Get Cluster Summary
    ↓
Organize by Cluster
    ↓
Calculate Statistics
    ↓
Return Summary
```

### 5. **Analytics Flow**
```
GET /analytics/dashboard-summary
    ↓
Parallel Queries:
├── Total Sales Count
├── Date Range
├── Monthly Aggregation
├── Top Products
└── Inventory Analysis
    ↓
Combine Results
    ↓
Format Response
    ↓
Return to Client
```

---

## Technology Stack

### Backend
```
FastAPI 0.111.1
  ├── uvicorn (ASGI server)
  ├── pydantic (validation)
  └── SQLAlchemy 2.0.19 (ORM)

Database
  └── SQLite (development)
      PostgreSQL (production)

Machine Learning
  ├── scikit-learn 1.3.2
  │   ├── RandomForestRegressor
  │   ├── GradientBoostingRegressor
  │   ├── ExtraTreesRegressor
  │   ├── KMeans
  │   └── MinMaxScaler
  │
  ├── TensorFlow 2.13.0 / Keras 2.13.0
  │   ├── LSTM
  │   └── GRU
  │
  ├── pandas 2.2.2
  ├── numpy 1.24.3
  ├── scipy 1.11.4
  └── joblib 1.3.2

Logging & Monitoring
  ├── python-json-logger 2.0.7
  └── python-dotenv 1.0.0
```

### Frontend
```
React
  ├── react-dom
  └── react-router

Styling
  ├── Tailwind CSS
  └── postcss

Charting
  └── Recharts

HTTP Client
  └── axios

Build Tool
  ├── Create React App
  └── webpack
```

---

## Clean Architecture Pattern

### Layer Structure
```
┌─────────────────────────────────┐
│   Presentation Layer            │ (FastAPI routes)
├─────────────────────────────────┤
│   Business Logic Layer          │ (Services)
├─────────────────────────────────┤
│   Data Access Layer             │ (CRUD, Repository)
├─────────────────────────────────┤
│   Data Layer                    │ (Models, DB)
└─────────────────────────────────┘
```

### Dependency Flow
```
Routes → Services → Repository/CRUD → Models → Database

Only downward dependencies allowed (no circular)
```

### Benefits
- ✅ Testability - Each layer can be tested independently
- ✅ Maintainability - Changes isolated to specific layers
- ✅ Scalability - Easy to add new features
- ✅ Reusability - Services can be used by multiple routes
- ✅ Flexibility - Easy to swap implementations

---

## Error Handling Architecture

```
Request
    ↓
Route Handler
    ↓
Business Logic
    ↓ (Exception)
├── BismarException
│   ├── ValidationError
│   ├── DataNotFoundError
│   ├── ModelTrainingError
│   ├── PredictionError
│   ├── ClusteringError
│   └── InsufficientDataError
│
↓
Global Exception Handler
    ↓
Log Error (JSON + Console)
    ↓
Format Error Response
    ↓
Return HTTP Error
    ↓
Client
```

---

## Logging Architecture

```
Application Code
    ↓
get_logger("module_name")
    ↓
┌───────────────────────────────┐
│   Logger Handler Chain        │
├───────────────────────────────┤
│ ├── Console Handler (INFO+)   │
│ ├── JSON File Handler         │
│ │   (app.log, rotated)        │
│ └── Error File Handler        │
│     (error.log, rotated)      │
└───────────────────────────────┘
    ↓
Log Output
```

---

## Deployment Architecture

### Development
```
Single Machine
├── Frontend (npm start) → localhost:3000
├── Backend (uvicorn) → localhost:8000
└── SQLite Database (local file)
```

### Production (Recommended)
```
Load Balancer (Nginx)
    ↓
┌─────────────────────────────┐
│  API Server Cluster (3-5)   │
├─────────────────────────────┤
│  uvicorn (gunicorn+uvicorn) │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│  Database Server            │
├─────────────────────────────┤
│  PostgreSQL (High Availability)
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│  Cache Layer                │
├─────────────────────────────┤
│  Redis (for model predictions)
└─────────────────────────────┘

CDN → Frontend Static Assets (React build)
```

---

## Scaling Strategies

### 1. Horizontal Scaling
- Multiple API instances behind load balancer
- Session-less API (stateless)
- Shared database and cache

### 2. Vertical Scaling
- Increase server resources (CPU, RAM)
- Better database indexing
- Model optimization

### 3. Caching Strategy
```python
# Cache ML predictions
@app.get("/analytics/dashboard-summary")
@cache(expire=300)  # Cache for 5 minutes
def dashboard_summary():
    ...
```

### 4. Database Optimization
```sql
-- Add indexes for frequent queries
CREATE INDEX idx_sales_tanggal ON sales(tanggal);
CREATE INDEX idx_sales_product ON sales(nama_barang);
CREATE INDEX idx_sales_kategori ON sales(kategori);

-- Materialized views for aggregations
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT DATE_TRUNC('month', tanggal) AS month,
       SUM(kuantitas) AS total_qty
FROM sales
GROUP BY DATE_TRUNC('month', tanggal);
```

---

## Security Architecture

### 1. Input Validation
```python
from pydantic import BaseModel, validator

class SalesCreate(BaseModel):
    kuantitas: int = Field(..., ge=0)  # Positive only
    tanggal: datetime = Field(...)
    
    @validator('kuantitas')
    def validate_qty(cls, v):
        if v > 10000:
            raise ValueError('Quantity too high')
        return v
```

### 2. API Security
```python
# CORS Restriction
CORS_ORIGINS = ["https://yourdomain.com"]

# Rate Limiting
@limiter.limit("100/minute")
def create_sales():
    ...

# JWT Authentication
@app.post("/auth/login")
def login(credentials):
    token = create_jwt_token(credentials)
    return {"access_token": token}
```

### 3. Database Security
- Use connection pooling
- Parameterized queries (SQLAlchemy prevents SQL injection)
- Encrypt sensitive data at rest

---

## Monitoring & Observability

### Metrics to Track
- API response times
- Error rates
- Model prediction accuracy
- Database query times
- Cache hit rates

### Implementation
```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_time = Histogram('prediction_seconds', 'Prediction time')

@prediction_time.time()
def make_prediction():
    prediction_counter.inc()
    ...
```

---

## Future Architecture Improvements

1. **Message Queue** - RabbitMQ/Kafka for async jobs
2. **Microservices** - Separate ML service
3. **API Gateway** - Kong/AWS API Gateway
4. **Container Orchestration** - Kubernetes
5. **Monitoring** - Prometheus + Grafana
6. **Tracing** - Jaeger for distributed tracing

---

See [README.md](README.md) and [API.md](API.md) for more details.
