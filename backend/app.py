from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Allow this module to work both when used as a package (backend.app)
# and when run directly from the backend directory (uvicorn app:app).
try:
    from . import crud, database, ml_model, models, populate_prices, dataset_routes
    from .schemas import (
        Product,
        ProductPrediction,
        ProductPredictionRequest,
        Sales,
        SalesCreate,
        SalesUpdate,
    )
    from .seed import seed_sales_from_csv
    from .ai import router as ai_router
    from .analytics import router as analytics_router
    from .deep_learning import router as deeplearning_router
    from .clustering import router as clustering_router
    from .logger import get_logger
    from .exceptions import BismarException
    from .config import settings
except ImportError:  # pragma: no cover
    import crud, database, ml_model, models, populate_prices, dataset_routes
    from schemas import (
        Product,
        ProductPrediction,
        ProductPredictionRequest,
        Sales,
        SalesCreate,
        SalesUpdate,
    )
    from seed import seed_sales_from_csv
    from ai import router as ai_router
    from analytics import router as analytics_router
    from deep_learning import router as deeplearning_router
    from clustering import router as clustering_router
    from logger import get_logger
    from exceptions import BismarException
    from config import settings

models.Base.metadata.create_all(bind=database.engine)

logger = get_logger("app")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-Powered Sales Intelligence Platform with Ensemble ML, Deep Learning, and Analytics",
)

# Add CORS middleware with specific origins restriction
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(BismarException)
async def bismar_exception_handler(request: Request, exc: BismarException):
    """Handle custom Bismar exceptions."""
    logger.error(f"BismarException: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Mount routers
app.include_router(ai_router)
app.include_router(analytics_router)
app.include_router(deeplearning_router)
app.include_router(clustering_router)
app.include_router(dataset_routes.router)

# Dependency

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api-info")
def api_info():
    """Get API information and available endpoints."""
    return {
        "api": {
            "title": settings.API_TITLE,
            "version": settings.API_VERSION,
            "description": "AI-Powered Sales Intelligence Platform"
        },
        "endpoints": {
            "sales": {
                "description": "CRUD operations for sales records",
                "paths": [
                    "GET /sales - List all sales",
                    "POST /sales - Create new sale",
                    "GET /sales/{id} - Get specific sale",
                    "PUT /sales/{id} - Update sale",
                    "DELETE /sales/{id} - Delete sale"
                ]
            },
            "analytics": {
                "description": "Advanced sales analytics and insights",
                "paths": [
                    "GET /analytics/monthly-sales",
                    "GET /analytics/product-performance",
                    "GET /analytics/sales-trend",
                    "GET /analytics/inventory-insights",
                    "GET /analytics/dashboard-summary"
                ]
            },
            "deep_learning": {
                "description": "Deep learning forecasting (LSTM/GRU)",
                "paths": [
                    "GET /deep-learning/predict/lstm",
                    "GET /deep-learning/predict/gru",
                    "GET /deep-learning/predict/ensemble-comparison"
                ]
            },
            "clustering": {
                "description": "Product segmentation (Fast/Medium/Slow Moving)",
                "paths": [
                    "GET /clustering/summary",
                    "GET /clustering/fast-moving",
                    "GET /clustering/medium-moving",
                    "GET /clustering/slow-moving"
                ]
            }
        }
    }


@app.post("/sales", response_model=Sales)
def create_sales(sales: SalesCreate, db: Session = Depends(get_db)):
    """Create a new sales record."""
    try:
        return crud.create_sales(db=db, sales=sales)
    except Exception as e:
        logger.error(f"Error creating sales: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create sales record")


@app.get("/sales", response_model=list[Sales])
def read_sales(db: Session = Depends(get_db)):
    """Get all sales records."""
    try:
        return crud.get_sales(db=db)
    except Exception as e:
        logger.error(f"Error reading sales: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sales records")


@app.get("/sales/monthly")
def get_monthly_sales(db: Session = Depends(get_db)):
    """Return aggregated monthly sales (kuantitas)"""
    try:
        return crud.get_monthly_sales(db=db)
    except Exception as e:
        logger.error(f"Error getting monthly sales: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monthly sales")


@app.on_event("startup")
def startup_seed_data():
    """Ensure master_sales.csv exists, and seed database from it if empty."""
    import shutil
    project_root = Path(__file__).resolve().parents[1]
    dataset_dir = project_root / "dataset"
    original_csv = dataset_dir / "clean_data_bismar_penjualan.csv"
    master_sales_csv = dataset_dir / "master_sales.csv"
    pricing_path = dataset_dir / "Data2.csv"

    # Copy clean bismar data to master_sales if master doesn't exist yet
    if not master_sales_csv.exists() and original_csv.exists():
        try:
            shutil.copy(original_csv, master_sales_csv)
            logger.info("Initialized master_sales.csv from clean_data_bismar_penjualan.csv")
        except Exception as e:
            logger.error(f"Failed to initialize master_sales.csv: {e}")

    with database.SessionLocal() as db:
        # Seed from master_sales if available, otherwise original_csv
        seed_source = master_sales_csv if master_sales_csv.exists() else original_csv
        if seed_source.exists():
            seed_sales_from_csv(db, seed_source)
        try:
            populate_prices.populate_prices_from_csv(pricing_path)
        except Exception as e:
            logger.error(f"Error populating prices at startup: {str(e)}")


@app.post("/sales/seed")
def seed_sales(force: bool = False):
    """Seed sales data from CSV.

    Use `?force=true` to reload CSV and overwrite existing data.
    """
    data_path = Path(__file__).resolve().parents[1] / "dataset" / "clean_data_bismar_penjualan.csv"
    with database.SessionLocal() as db:
        inserted = seed_sales_from_csv(db, data_path, force=force)
    return {"inserted": inserted}


@app.get("/sales/predict")
def predict_next_month_sales(db: Session = Depends(get_db)):
    """Train model and predict next month sales."""
    prediction = ml_model.predict_next_month_sales(db=db)
    return {"predicted_sales_next_month": prediction}


@app.get("/products", response_model=list[Product])
def list_products(db: Session = Depends(get_db)):
    """List unique products available in sales history."""
    return crud.get_products(db=db)


@app.post("/predict-product", response_model=ProductPrediction)
def predict_product(prediction: ProductPredictionRequest, db: Session = Depends(get_db)):
    """Predict quantity for a product on a specific date or date range."""

    def _get_average_price(product_name: str) -> float:
        """Get average price for a product from sales history."""
        try:
            result = db.query(models.Sales).filter(
                models.Sales.nama_barang == product_name,
                models.Sales.harga_satuan > 0
            ).first()
            if result and result.harga_satuan:
                return float(result.harga_satuan)
        except Exception:
            pass
        return 0.0

    def _predict_for_date(date_str: str, product_name: str) -> dict:
        try:
            result = ml_model.predict_product_sales(
                date_str=date_str,
                product_name=product_name,
            )
            # Calculate revenue: qty × price × (1 - discount%)
            price = _get_average_price(product_name)
            estimated_revenue = result["predicted_qty"] * price
            
            return {
                "predicted_qty": result["predicted_qty"],
                "estimated_revenue": estimated_revenue,
                "unit_price": price,
            }
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"Prediction failed for {product_name} on {date_str}: {str(e)}")
            return {"predicted_qty": 0, "estimated_revenue": 0.0, "unit_price": 0.0}

    # Determine date range
    start_date = prediction.date
    end_date = prediction.end_date or prediction.date
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be equal or after date")

    # Support an "all products" option in the frontend.
    if prediction.product_id == "ALL":
        products = crud.get_products(db=db)
        if not products:
            raise HTTPException(status_code=404, detail="No products available")

        total_qty = 0
        total_revenue = 0.0
        details: list[dict] = []
        current = start_date

        while current <= end_date:
            for prod in products:
                result = _predict_for_date(current.isoformat(), prod["nama_barang"])
                total_qty += result["predicted_qty"]
                total_revenue += result["estimated_revenue"]

                # Keep per-product details to display for the user.
                detail = next((d for d in details if d["product"] == prod["nama_barang"]), None)
                if detail is None:
                    detail = {
                        "product": prod["nama_barang"],
                        "predicted_qty": 0,
                        "estimated_revenue": 0.0,
                    }
                    details.append(detail)
                detail["predicted_qty"] += result["predicted_qty"]
                detail["estimated_revenue"] += result["estimated_revenue"]

            current = current + timedelta(days=1)

        return {
            "product": "Semua Produk",
            "predicted_qty": total_qty,
            "estimated_revenue": total_revenue,
            "details": details,
        }

    product = crud.get_product_by_code(db=db, kode_produk=prediction.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    total_qty = 0
    total_revenue = 0.0
    current = start_date
    while current <= end_date:
        result = _predict_for_date(current.isoformat(), product["nama_barang"])
        total_qty += result["predicted_qty"]
        total_revenue += result["estimated_revenue"]
        current = current + timedelta(days=1)

    return {
        "product": product["nama_barang"],
        "predicted_qty": total_qty,
        "estimated_revenue": total_revenue,
    }


@app.get("/sales/{sales_id}", response_model=Sales)
def read_sales_by_id(sales_id: int, db: Session = Depends(get_db)):
    db_sales = crud.get_sales_by_id(db=db, sales_id=sales_id)
    if not db_sales:
        raise HTTPException(status_code=404, detail="Sales record not found")
    return db_sales


@app.put("/sales/{sales_id}", response_model=Sales)
def update_sales(sales_id: int, sales: SalesUpdate, db: Session = Depends(get_db)):
    db_sales = crud.get_sales_by_id(db=db, sales_id=sales_id)
    if not db_sales:
        raise HTTPException(status_code=404, detail="Sales record not found")
    return crud.update_sales(db=db, sales=db_sales, sales_in=sales)


@app.delete("/sales/{sales_id}")
def delete_sales(sales_id: int, db: Session = Depends(get_db)):
    db_sales = crud.get_sales_by_id(db=db, sales_id=sales_id)
    if not db_sales:
        raise HTTPException(status_code=404, detail="Sales record not found")
    crud.delete_sales(db=db, sales=db_sales)
    return {"detail": "Sales record deleted"}
