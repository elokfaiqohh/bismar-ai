# 📚 API Documentation - Indo Bismar AI Forecast

Complete API reference with examples for all endpoints.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. Add JWT in production.

---

## General Response Format

### Success Response
```json
{
  "data": {...},
  "status": "success",
  "timestamp": "2026-06-06T10:30:00"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status": "error",
  "timestamp": "2026-06-06T10:30:00"
}
```

---

## Endpoints

### System & Health

#### Get Health Status
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-06-06T10:30:00Z"
}
```

#### Get API Info
```http
GET /api-info
```

Response:
```json
{
  "api": {
    "title": "Indo Bismar AI Forecast",
    "version": "2.0.0",
    "description": "AI-Powered Sales Intelligence Platform"
  },
  "endpoints": {
    "sales": {...},
    "analytics": {...},
    "deep_learning": {...},
    "clustering": {...}
  }
}
```

---

### Sales Management

#### List All Sales
```http
GET /sales
```

Response:
```json
[
  {
    "id": 1,
    "tanggal": "2026-01-15T10:30:00",
    "nama_barang": "Product A",
    "kuantitas": 50,
    "kategori": "Electronics",
    "tipe_transaksi": "Sale",
    ...
  }
]
```

#### Create Sales Record
```http
POST /sales
Content-Type: application/json

{
  "tanggal": "2026-06-06T10:30:00",
  "nama_barang": "Product A",
  "tipe_transaksi": "Sale",
  "kuantitas": 25,
  "satuan": "pcs",
  "day_of_week": 3,
  "nama_hari": "Rabu",
  "day_type": "Weekday",
  "tx_order": 1,
  "total_per_day": 100,
  "waktu_ratio": 0.25,
  "waktu": "10:30-11:00",
  "kategori": "Electronics"
}
```

Response: `201 Created`
```json
{
  "id": 1234,
  "tanggal": "2026-06-06T10:30:00",
  ...
}
```

#### Get Specific Sale
```http
GET /sales/{id}
```

Parameters:
- `id` (integer) - Sale ID

Response: `200 OK`
```json
{
  "id": 1,
  "tanggal": "2026-01-15T10:30:00",
  ...
}
```

#### Update Sale
```http
PUT /sales/{id}
Content-Type: application/json

{
  "kuantitas": 30
}
```

Response: `200 OK`

#### Delete Sale
```http
DELETE /sales/{id}
```

Response: `200 OK`
```json
{"detail": "Sales record deleted"}
```

---

### Analytics Endpoints

#### Get Monthly Sales
```http
GET /analytics/monthly-sales
```

Response:
```json
[
  {
    "month": "2026-01",
    "penjualan_bersih": 5000,
    "total_kuantitas": 5000
  },
  {
    "month": "2026-02",
    "penjualan_bersih": 6500,
    "total_kuantitas": 6500
  }
]
```

#### Get Sales Trend
```http
GET /analytics/sales-trend?months_back=12&frequency=month
```

Query Parameters:
- `months_back` (integer, 1-60, default 12) - Months to look back
- `frequency` (string, default "month") - 'day', 'week', or 'month'

Response:
```json
{
  "frequency": "month",
  "months_back": 12,
  "data": [
    {
      "tanggal": "2025-06-01",
      "total_qty": 5000,
      "avg_qty": 166.67,
      "max_qty": 500,
      "min_qty": 10,
      "num_transactions": 30
    }
  ]
}
```

#### Get Product Performance
```http
GET /analytics/product-performance?limit=10
```

Query Parameters:
- `limit` (integer, 1-100, default 20) - Number of top products

Response:
```json
{
  "count": 10,
  "products": [
    {
      "nama_barang": "Product A",
      "kategori": "Electronics",
      "total_qty": 5000,
      "num_transactions": 250,
      "days_since_last_sale": 2,
      "product_age_days": 365
    }
  ]
}
```

#### Get Category Performance
```http
GET /analytics/category-performance
```

Response:
```json
{
  "count": 5,
  "categories": [
    {
      "kategori": "Electronics",
      "total_qty": 15000,
      "num_products": 12,
      "num_transactions": 750
    }
  ]
}
```

#### Get Daily Statistics
```http
GET /analytics/daily-statistics
```

Response:
```json
{
  "days": [
    {
      "day": "Senin",
      "day_of_week": 0,
      "total_qty": 2000,
      "num_transactions": 100,
      "avg_qty_per_transaction": 20.0
    }
  ]
}
```

#### Get Inventory Insights
```http
GET /analytics/inventory-insights?dead_stock_days=60
```

Query Parameters:
- `dead_stock_days` (integer, 30-365, default 60) - Days without sales

Response:
```json
{
  "dead_stock_count": 2,
  "slow_movers_count": 5,
  "active_products_count": 45,
  "dead_stock": [
    {
      "product": "Old Product",
      "days_without_sales": 120,
      "total_qty_sold": 50
    }
  ],
  "slow_movers": [...],
  "active": [...]
}
```

#### Get Time of Day Analysis
```http
GET /analytics/time-of-day-analysis
```

Response:
```json
{
  "time_slots": [
    {
      "time_slot": "08:00-09:00",
      "total_qty": 500,
      "num_transactions": 50,
      "avg_qty": 10.0
    }
  ]
}
```

#### Get Dashboard Summary
```http
GET /analytics/dashboard-summary
```

Response:
```json
{
  "summary": {
    "total_sales_records": 2500,
    "date_range": {
      "min_date": "2025-01-01T00:00:00",
      "max_date": "2026-06-06T23:59:59"
    },
    "avg_monthly_sales": 5250.0,
    "total_months": 18
  },
  "top_products": [...],
  "inventory": {
    "dead_stock_count": 2,
    "slow_movers_count": 5,
    "active_products_count": 45
  }
}
```

---

### Deep Learning Predictions

#### Get LSTM Prediction
```http
GET /deep-learning/predict/lstm
```

Response:
```json
{
  "model": "LSTM",
  "predicted_sales_next_month": 6234.75,
  "data_points": 24,
  "method": "Long Short-Term Memory Neural Network"
}
```

Status Codes:
- `200` - Success
- `400` - Insufficient data
- `503` - Model not available

#### Get GRU Prediction
```http
GET /deep-learning/predict/gru
```

Response:
```json
{
  "model": "GRU",
  "predicted_sales_next_month": 6100.50,
  "data_points": 24,
  "method": "Gated Recurrent Unit Neural Network"
}
```

#### Compare All Predictions
```http
GET /deep-learning/predict/ensemble-comparison
```

Response:
```json
{
  "predictions": {
    "ensemble": 5890.25,
    "lstm": 6234.75,
    "gru": 6100.50,
    "average": 6075.17,
    "best_estimate": 5890.25
  },
  "data_points": 24,
  "description": "Comparison of different forecasting models"
}
```

#### Get Deep Learning Model Info
```http
GET /deep-learning/model-info
```

Response:
```json
{
  "lstm": {
    "available": true,
    "type": "Long Short-Term Memory",
    "description": "Excellent for long-term dependencies in time series",
    "advantages": ["Handles long sequences", ...],
    "disadvantages": ["Slower training", ...]
  },
  "gru": {...},
  "ensemble": {...}
}
```

#### Get Deep Learning Status
```http
GET /deep-learning/status
```

Response:
```json
{
  "lstm_available": true,
  "gru_available": true,
  "clustering_available": true
}
```

---

### Product Clustering

#### Get Cluster Summary
```http
GET /clustering/summary
```

Response:
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "cluster_name": "Fast Moving",
      "num_products": 15,
      "avg_total_qty": 8500.0,
      "avg_daily_qty": 45.3,
      "avg_transactions": 250,
      "products": ["Product A", "Product B", ...]
    },
    {
      "cluster_id": 1,
      "cluster_name": "Medium Moving",
      "num_products": 8,
      ...
    },
    {
      "cluster_id": 2,
      "cluster_name": "Slow Moving",
      "num_products": 5,
      ...
    }
  ],
  "description": "Product segmentation based on sales velocity"
}
```

#### Get Product Cluster Info
```http
GET /clustering/product/{product_name}
```

Parameters:
- `product_name` (string) - Product name

Response:
```json
{
  "product": "Product A",
  "cluster_id": 0,
  "cluster_name": "Fast Moving",
  "total_qty": 8500,
  "avg_daily_qty": 45.3,
  "num_transactions": 250
}
```

#### Get Fast Moving Products
```http
GET /clustering/fast-moving
```

Response:
```json
{
  "category": "Fast Moving",
  "count": 15,
  "products": [
    {
      "product": "Product A",
      "total_qty": 8500,
      "avg_daily_qty": 45.3
    }
  ]
}
```

#### Get Medium Moving Products
```http
GET /clustering/medium-moving
```

Response:
```json
{
  "category": "Medium Moving",
  "count": 8,
  "products": [...]
}
```

#### Get Slow Moving Products
```http
GET /clustering/slow-moving
```

Response:
```json
{
  "category": "Slow Moving",
  "count": 5,
  "products": [...]
}
```

#### Get Clustering Info
```http
GET /clustering/info
```

Response:
```json
{
  "description": "Product clustering segments products into three categories",
  "categories": {
    "fast_moving": {
      "description": "Products with high sales velocity",
      "recommendation": "Maintain stock levels, focus on distribution"
    },
    ...
  },
  "method": "K-Means clustering with features: ...",
  "lookback_period": "90 days"
}
```

#### Get Clustering Status
```http
GET /clustering/status
```

Response:
```json
{
  "clustering_available": true
}
```

---

### AI/ML Insights

#### Get Restock Recommendation
```http
POST /ai/restock-recommendation
Content-Type: application/json

{
  "product_id": "Product A",
  "current_stock": 100,
  "date": "2026-06-06"
}
```

Response:
```json
{
  "product": "Product A",
  "predicted_demand": 250,
  "current_stock": 100,
  "recommended_restock": 150
}
```

#### Get Top Products Tomorrow
```http
GET /ai/top-products
```

Response:
```json
[
  {
    "product": "Product A",
    "predicted_qty": 450
  },
  {
    "product": "Product B",
    "predicted_qty": 380
  }
]
```

#### Get Dead Stock Products
```http
GET /ai/dead-stock
```

Response:
```json
[
  {
    "product": "Old Product",
    "last_sale": "2026-03-20",
    "days_without_sales": 78,
    "status": "Potential Dead Stock"
  }
]
```

#### Run Discount Simulation
```http
POST /ai/discount-simulation
Content-Type: application/json

{
  "product_id": "Product A",
  "date": "2026-06-07"
}
```

Response:
```json
[
  {
    "discount": 0.0,
    "predicted_qty": 250
  },
  {
    "discount": 5.0,
    "predicted_qty": 268
  },
  {
    "discount": 10.0,
    "predicted_qty": 287
  },
  {
    "discount": 15.0,
    "predicted_qty": 306
  }
]
```

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 400 | Bad Request | Check parameters, invalid data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Check server logs |
| 503 | Service Unavailable | Model not trained/loaded |

---

## Rate Limiting

Currently no rate limiting. Add in production:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/predict")
@limiter.limit("10/minute")
async def predict():
    ...
```

---

## Best Practices

### 1. Error Handling
Always check for errors in responses:
```python
import requests

response = requests.get("http://localhost:8000/analytics/sales-trend")
if response.status_code == 200:
    data = response.json()
else:
    print(f"Error: {response.status_code}")
    print(response.json()["detail"])
```

### 2. Pagination
For large datasets, implement pagination:
```http
GET /sales?skip=0&limit=50
```

### 3. Caching
Cache responses when appropriate:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_clustering_summary():
    return requests.get(".../clustering/summary").json()
```

### 4. Async Requests
Use async for multiple concurrent requests:
```python
import asyncio
import aiohttp

async def fetch_all():
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.get("http://localhost:8000/analytics/monthly-sales"),
            session.get("http://localhost:8000/analytics/product-performance"),
        ]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]
```

---

## Testing Endpoints

### cURL Examples
```bash
# Health check
curl http://localhost:8000/health

# Get sales
curl http://localhost:8000/sales

# LSTM prediction
curl http://localhost:8000/deep-learning/predict/lstm

# Clustering summary
curl http://localhost:8000/clustering/summary

# Product performance
curl "http://localhost:8000/analytics/product-performance?limit=10"
```

### Postman Collection
Import this into Postman to test all endpoints:
```json
{
  "info": {
    "name": "Indo Bismar API",
    "version": "2.0.0"
  },
  "item": [
    {
      "name": "Health",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    }
  ]
}
```

---

See [README.md](README.md) for more information.
