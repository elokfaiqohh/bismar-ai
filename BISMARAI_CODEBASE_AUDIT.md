# BismarAI Codebase Audit

## 1. Executive Summary

BismarAI is a sales-forecasting and business-intelligence web application implemented as a FastAPI backend plus a React frontend. Its implemented purpose is to ingest sales transaction data, store it in a SQLite database, train and serve forecasting models, and present dashboards for forecasting, analytics, inventory signals, and dataset management.

Based on the source code, the target users are operational users and administrators who work with sales data, product forecasting, and inventory planning. The main implemented capabilities are:

- Sales data ingestion and management
- Monthly and product-level sales forecasting
- AI-driven restock recommendations
- Dead-stock and slow-moving product detection
- Dataset upload, validation, import, backup, and restore
- Analytics dashboards for revenue, sales trends, and product performance

## 2. System Overview

The implemented architecture is a layered web application:

Dataset CSV
↓
Dataset validation and import routes
↓
SQLite database via SQLAlchemy
↓
CRUD and analytics services
↓
Machine learning services
↓
FastAPI endpoints
↓
React dashboard pages

The codebase implements the following runtime flow:

1. The backend starts and creates database tables.
2. On startup, it seeds sales data from a CSV file into the SQLite database and populates prices from a pricing CSV.
3. The frontend calls backend APIs for sales, forecasting, AI insights, analytics, and dataset management.
4. The backend exposes a set of routers for analytics, AI features, deep learning, clustering, and dataset management.
5. The ML pipeline includes:
   - an ensemble regressor for monthly sales forecasting,
   - a product-level regressor for product/date prediction,
   - LSTM and GRU models for sequence-based forecasting,
   - K-Means clustering for product segmentation.

## 3. Technology Stack

### Frontend
- React 18
- React Router DOM
- Tailwind CSS
- Recharts
- Framer Motion
- Lucide React
- Sonner toast notifications
- Axios

### Backend
- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic and Pydantic Settings
- Pandas
- NumPy
- scikit-learn
- Joblib
- TensorFlow/Keras for LSTM and GRU

### Database
- SQLite via SQLAlchemy
- One primary table: sales

### Machine Learning
- RandomForestRegressor
- GradientBoostingRegressor
- ExtraTreesRegressor
- VotingRegressor
- LSTM
- GRU
- KMeans
- StandardScaler and MinMaxScaler

### Utilities
- Python logging with JSON file logging
- Background task support for model retraining
- CSV-based dataset import and backup handling

### Authentication
- Not implemented in the source code.

### Deployment
- Local development scripts and deployment scripts are present.
- No containerization or cloud deployment configuration is implemented in the repository files examined.

## 4. Machine Learning Audit

### Models implemented

1. Product-level forecasting model
   - The training script evaluates three regressors:
     - Random Forest
     - Gradient Boosting
     - Extra Trees
   - It selects the best-performing model by test R2 and saves it to a pickle file.
   - This model is used by the product prediction endpoint.

2. Monthly ensemble forecasting model
   - The monthly forecasting function uses a VotingRegressor composed of:
     - Random Forest
     - Gradient Boosting
     - Extra Trees
   - It predicts the next month using a single feature: month index.

3. Deep learning forecasting models
   - LSTM model implemented in the deep learning module.
   - GRU model implemented in the deep learning module.
   - Both use a lookback window of 12 months and MinMax scaling.

4. Clustering model
   - K-Means clustering is implemented for product segmentation into Fast, Medium, and Slow Moving categories.

### How they interact

- The product-level model is used for date-specific product forecasting.
- The monthly ensemble model is used by the general sales forecast endpoint.
- The LSTM and GRU models are exposed through dedicated deep-learning endpoints.
- The clustering model is used by the clustering API endpoints.
- The AI dashboard consumes the outputs of the product prediction and analytics APIs, but it does not orchestrate the models directly.

### Which one performs prediction

- Product prediction endpoint: uses the trained product-level model.
- General forecast endpoint: uses the monthly ensemble model.
- Deep-learning endpoints: use LSTM or GRU when available.
- Clustering endpoints: use the K-Means model.

### Ensemble architecture

The implemented ensemble architecture is a VotingRegressor combining Random Forest, Gradient Boosting, and Extra Trees.

## 5. Feature Engineering Audit

### Original columns used by the dataset import pipeline
The import flow expects these columns:
- Tanggal
- Nama_Barang
- Tipe_Transaksi
- Kuantitas
- Satuan
- DayOfWeek
- NamaHari
- DayType
- TxOrder
- TotalPerDay
- WaktuRatio
- Waktu
- Kategori

### Engineered features

In the product training pipeline:
- day
- month
- year
- DayOfWeek
- Nama_Barang_code
- Kategori_code
- DayType_code

These are derived from the source dataset and used as model inputs.

### Encoding
- Categorical columns are converted to pandas categorical types.
- Label encoding is applied with category codes for:
  - Nama_Barang
  - Kategori
  - DayType

### Scaling
- LSTM and GRU models use MinMaxScaler.
- Clustering uses StandardScaler.

### Aggregation
- Monthly forecasting aggregates transaction quantity by year-month.
- Clustering aggregates per-product metrics such as total quantity, average daily quantity, transaction count, sales standard deviation, days since last sale, and product age.

### Date features
- The training scripts derive day, month, year, and day-of-week values from the transaction date.

### Category mapping
- The product model file stores mappings for product names, categories, and day types.
- A product-to-category mapping is also stored for inference.

### Missing value handling
- The CSV seeding logic does not implement a sophisticated imputation strategy.
- Missing or invalid dates are dropped during import/seeding.
- Numeric parsing failures default to 0 or 0.0.

## 6. Training Pipeline

### How training starts
Training is started manually through:
- the retraining route in the dataset router, or
- the standalone scripts such as setup_and_train.py and train_product_model.py.

### Where data is loaded from
- The training pipeline reads the CSV dataset from the dataset folder.
- The default training data path is dataset/master_sales.csv.
- The backend also seeds the database from the CSV during startup.

### How preprocessing happens
- CSV headers are normalized to lowercase in the seeding layer.
- The training script converts the date column to datetime.
- It creates derived date features.
- It encodes categorical values.
- It splits data into train and test sets.

### How models are trained
- Product-level model: three regressors are trained and compared.
- Monthly ensemble model: a VotingRegressor is trained on monthly aggregated data.
- LSTM and GRU: sequence windows are created from monthly data and the models are fit.
- Clustering: K-Means is fit on engineered product features.

### Where models are saved
- Product-level model: backend/model_product_sales.pkl
- LSTM model: backend/models/lstm_model.h5 plus a scaler pickle
- GRU model: backend/models/gru_model.h5 plus a scaler pickle
- Clustering model: backend/models/kmeans_model.pkl

### How retraining works
- The dataset management API exposes a retraining endpoint.
- It triggers background retraining of the product-level model only.
- It does not retrain the LSTM/GRU/clustering models through that endpoint.

## 7. Prediction Pipeline

### How prediction works
- The frontend sends a prediction request to the backend.
- The backend chooses the relevant prediction path:
  - product/date prediction via the product model,
  - monthly sales prediction via the ensemble model,
  - deep learning prediction via LSTM/GRU.

### Which API is called
- Product-level prediction: POST /predict-product
- Monthly forecast: GET /sales/predict
- LSTM: GET /deep-learning/predict/lstm
- GRU: GET /deep-learning/predict/gru
- Ensemble comparison: GET /deep-learning/predict/ensemble-comparison

### How data flows into the model
- Product prediction uses a date plus product name and maps that into encoded features.
- Monthly forecasting aggregates sales by month and trains a model on month index to predict the next month.
- Deep learning uses the historical monthly sales array as a time series input.

### How prediction results are generated
- The product model returns a predicted quantity and the backend calculates estimated revenue using the average stored price for the product.
- The monthly forecast returns a scalar predicted sales value.
- The deep-learning routes return model-specific forecasts.

## 8. API Documentation

### Core application endpoints

- GET /health
  - Purpose: health check
  - Response: status, version, timestamp
  - Authorization: none
  - Frontend usage: none

- GET /api-info
  - Purpose: returns API metadata and available endpoint groups
  - Response: API title, version, endpoint descriptions
  - Authorization: none
  - Frontend usage: none

### Sales endpoints

- POST /sales
  - Purpose: create a sales record
  - Request: sales payload
  - Response: created sales record
  - Authorization: none
  - Frontend page: Sales page

- GET /sales
  - Purpose: list all sales records
  - Response: list of sales records
  - Authorization: none
  - Frontend page: Sales page

- GET /sales/monthly
  - Purpose: aggregated monthly sales values
  - Response: monthly revenue/quantity summary
  - Authorization: none
  - Frontend page: Dashboard

- GET /sales/{id}
  - Purpose: fetch one sales record
  - Response: one sales record
  - Authorization: none
  - Frontend page: Sales page

- PUT /sales/{id}
  - Purpose: update a sales record
  - Response: updated sales record
  - Authorization: none
  - Frontend page: Sales page

- DELETE /sales/{id}
  - Purpose: delete a sales record
  - Response: confirmation payload
  - Authorization: none
  - Frontend page: Sales page

- POST /sales/seed
  - Purpose: seed sales data from CSV
  - Response: inserted row count
  - Authorization: none
  - Frontend page: none

- GET /sales/predict
  - Purpose: predict next month sales with the monthly ensemble model
  - Response: predicted sales value
  - Authorization: none
  - Frontend page: Dashboard

### Product prediction endpoint

- POST /predict-product
  - Purpose: predict quantity for a product on a single date or range of dates
  - Request: date, optional end_date, product_id
  - Response: aggregated quantity, estimated revenue, and optional details
  - Authorization: none
  - Frontend page: Prediction page

### Analytics endpoints

- GET /analytics/monthly-sales
- GET /analytics/product-sales
- GET /analytics/revenue-trend
- GET /analytics/branch-performance
- GET /analytics/sales-trend
- GET /analytics/product-performance
- GET /analytics/category-performance
- GET /analytics/daily-statistics
- GET /analytics/inventory-insights
- GET /analytics/time-of-day-analysis
- GET /analytics/dashboard-summary

All of these are implemented and used by the dashboard and AI dashboard pages. Authorization: none.

### AI endpoints

- POST /ai/restock-recommendation
- GET /ai/top-products
- GET /ai/dead-stock
- POST /ai/discount-simulation
- GET /ai/insights

These are used by the AI dashboard and are implemented without authentication.

### Deep-learning endpoints

- GET /deep-learning/status
- GET /deep-learning/predict/lstm
- GET /deep-learning/predict/gru
- GET /deep-learning/predict/ensemble-comparison
- GET /deep-learning/model-info

### Clustering endpoints

- GET /clustering/status
- GET /clustering/summary
- GET /clustering/product/{product_name}
- GET /clustering/fast-moving
- GET /clustering/medium-moving
- GET /clustering/slow-moving
- GET /clustering/info

### Dataset endpoints

- POST /api/dataset/upload
- POST /api/dataset/import
- GET /api/dataset/history
- GET /api/dataset/statistics
- POST /api/dataset/restore-latest
- POST /api/dataset/restore/{backup_id}
- POST /api/model/retrain

These are used by the dataset management page.

## 9. Database Audit

### Tables
The implemented schema contains one main table:
- sales

### Columns in the sales table
The model includes fields such as:
- id
- tanggal
- nama_barang
- tipe_transaksi
- kuantitas
- satuan
- day_of_week
- nama_hari
- day_type
- tx_order
- total_per_day
- waktu_ratio
- waktu
- kategori
- harga_satuan
- total_penjualan
- diskon
- penjualan_bersih

### Relationships
No explicit relationships, foreign keys, or joins between multiple tables are implemented. The system is effectively a single-table SQLite design.

### Data synchronization
The dataset import pipeline updates the CSV master file and syncs the database from it. The startup flow also seeds the database from CSV.

### Source of truth
The implementation uses both CSV and database:
- The dataset file under dataset acts as the managed source for imports, restores, and retraining.
- The SQLite database is used as the runtime data source for API responses and frontend pages.

## 10. Frontend Audit

### Dashboard page
- Shows KPIs such as total revenue, next-month prediction, product count, and dataset statistics.
- Displays monthly sales charts and AI insights cards.
- Calls the backend for monthly sales, prediction, top products, and dataset history.

### Sales page
- Displays sales records in a searchable, filterable table.
- Supports creating, editing, and deleting sales entries.
- Sends CRUD requests to the backend.

### Prediction page
- Lets users select a date or date range and a product.
- Sends prediction requests to the backend.
- Displays predicted quantity and estimated revenue.

### AI Dashboard page
- Displays AI-oriented features such as forecast summaries, restock recommendations, top products, dead stock, and insights.
- Calls the AI and analytics APIs.

### Dataset Management page
- Supports CSV upload and strict schema validation.
- Allows import in APPEND or REPLACE mode.
- Supports backup history, restore, and model retraining.

### Authentication
- No authentication or user management flow is present.

## 11. AI Features

The following AI capabilities are implemented in the source code:

- Sales forecasting for the next month
- Product-level demand prediction by date
- Ensemble forecasting using multiple regression models
- Deep learning forecasting with LSTM and GRU
- Product segmentation via K-Means clustering
- Restock recommendation based on predicted demand
- Dead-stock detection
- Inventory insight generation
- Insight generation from recent sales data
- Dataset validation and import automation
- Model retraining workflow

## 12. Current Limitations

### Missing features
- No authentication or authorization system.
- No user roles or permissions.
- No real-time streaming or background retraining schedule.

### Technical debt
- The codebase contains overlapping training and prediction logic in multiple modules.
- The monthly forecasting route trains a model on each request instead of loading a persisted model.
- The product model retraining route is separate from the deep learning and clustering training flows.

### Performance issues
- The monthly forecast endpoint retrains a model each time it is called.
- Some analytics computations iterate over all rows in Python rather than using SQL aggregations.
- Deep learning training is likely computationally heavy and may be slow in local environments.

### Security issues
- CORS is configured to allow all origins.
- No authentication is present.
- No explicit input sanitization beyond FastAPI/Pydantic validation.

### Architecture issues
- The system is tightly coupled around CSV and SQLite operations.
- The frontend hard-codes the backend URL to localhost:8000.
- The frontend contains some hard-coded performance labels that are not derived from actual model metrics.

### Maintainability problems
- Some routes and UI components contain hard-coded values and static display content that do not reflect the real model state.
- The discount simulation logic is explicitly described as a mock.

## 13. Project Strengths

- The project has a clear modular structure with separate routers and services.
- The backend exposes a broad set of forecasting and analytics APIs.
- The dataset management pipeline includes upload validation, import mode handling, backup generation, and restore capability.
- The frontend provides a coherent multi-page workflow for business users.
- The implementation includes multiple ML approaches rather than a single model approach.
- The codebase includes model persistence and model loading logic.

## 14. Suggested Future Improvements

### Short-term
- Add authentication and authorization.
- Replace hard-coded frontend metrics with real backend values.
- Persist and reuse the monthly ensemble model instead of retraining on each request.
- Add a configuration setting for backend URL and environment handling.

### Medium-term
- Implement a unified training pipeline that retrains all ML models consistently.
- Add automated model evaluation and monitoring.
- Add proper error handling and structured API response standards.
- Add tests for backend routes and frontend behavior.

### Long-term
- Move from SQLite to a production-grade database.
- Introduce batch or streaming data ingestion.
- Add MLOps capabilities such as experiment tracking, versioning, and deployment automation.
- Add role-based dashboards for different business users.

## 15. Final Project Summary

BismarAI is an AI-powered sales forecasting and analytics platform implemented as a FastAPI backend and React frontend. Its purpose is to help users manage sales data, forecast demand, detect inventory risks, and explore dataset-driven insights. The implementation uses a SQLite database for transactional storage, CSV-based dataset management for imports and backups, and several machine learning techniques including Random Forest, Gradient Boosting, Extra Trees, Voting Ensembles, LSTM, GRU, and K-Means clustering. Its business value lies in turning historical sales data into forecasting and inventory insights for operational decision-making. The system architecture is modular, with separate layers for database access, analytics, AI services, dataset workflows, and UI pages.
