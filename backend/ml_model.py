from datetime import datetime
from pathlib import Path
import logging

import joblib
import pandas as pd
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor,
    VotingRegressor
)

# Support running from within backend/ directory (as script) and as a package.
try:
    from . import models
except ImportError:  # pragma: no cover
    import models

# Setup logging
logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / "model_product_sales.pkl"


def _load_sales_dataframe(db) -> pd.DataFrame:
    """Load sales data from the database and return a pandas DataFrame."""
    results = db.query(models.Sales).all()
    data = [
        {
            "tanggal": r.tanggal,
                "kuantitas": float(r.kuantitas or 0.0),
        }
        for r in results
    ]

    df = pd.DataFrame(data)
    if df.empty:
        return df

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df


def _aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate kuantitas by year-month."""
    df = df.copy()
    df["month"] = df["tanggal"].dt.to_period("M").dt.to_timestamp()
    grouped = df.groupby("month").agg({"kuantitas": "sum"}).reset_index()
    grouped = grouped.sort_values("month")
    return grouped


def predict_next_month_sales(db) -> float:
    """Train an ensemble of 3 models on monthly sales and predict next month."""
    df = _load_sales_dataframe(db)
    if df.empty:
        return 0.0

    monthly = _aggregate_monthly(df)

    # Feature engineering: convert month to integer (months since epoch)
    monthly = monthly.copy()
    monthly["month_index"] = monthly["month"].dt.year * 12 + monthly["month"].dt.month

    # Create features and target
    X = monthly[["month_index"]].values
    y = monthly["kuantitas"].values

    if len(X) < 2:
        # Not enough data to train
        return float(y[-1] if len(y) else 0.0)

    # Gunakan VotingRegressor untuk menggabungkan 3 model sekaligus
    model = VotingRegressor(estimators=[
        ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
        ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
        ('et', ExtraTreesRegressor(n_estimators=100, random_state=42))
    ])
    
    model.fit(X, y)

    next_month_index = X[-1, 0] + 1
    prediction = model.predict([[next_month_index]])
    return float(prediction[0])


_cached_product_model = None


def _load_product_model():
    """Load the pretrained product model and encoding mappings."""
    global _cached_product_model
    if _cached_product_model is not None:
        return _cached_product_model

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Product model not found. Run `python train_product_model.py` to generate {MODEL_PATH}")

    data = joblib.load(MODEL_PATH)
    model = data.get("model")
    mapping_nama = data.get("nama_barang_mapping")
    mapping_kategori = data.get("kategori_mapping")
    mapping_daytype = data.get("daytype_mapping")
    product_to_kategori = data.get("product_to_kategori")
    
    if model is None or mapping_nama is None:
        raise ValueError("Invalid model file format.")

    logger.info(f"Model loaded: {len(mapping_nama)} products, {len(mapping_kategori)} categories, {len(mapping_daytype)} day types")
    
    rev_nama = {v: k for k, v in mapping_nama.items()}
    rev_kategori = {v: k for k, v in mapping_kategori.items()}
    rev_daytype = {v: k for k, v in mapping_daytype.items()}
    
    _cached_product_model = (model, rev_nama, rev_kategori, rev_daytype, product_to_kategori)
    return _cached_product_model


def predict_product_sales(date_str: str, product_name: str) -> dict:
    """Predict qty for a given product and date.

    Parameters
    ----------
    date_str: str
        ISO date string (YYYY-MM-DD)
    product_name: str
        nama_barang

    Returns
    -------
    dict
        {"predicted_qty": int}
    """
    logger.info(f"=== PREDICTION START ===")
    logger.info(f"Date: {date_str}, Product: {product_name}")
    
    try:
        model, rev_nama, rev_kategori, rev_daytype, product_to_kategori = _load_product_model()
        logger.info(f"✓ Model loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"✗ Model not found: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"✗ Invalid model format: {str(e)}")
        raise

    # Parse date
    try:
        dt = datetime.fromisoformat(date_str)
        day = dt.day
        month = dt.month
        year = dt.year
        day_of_week = dt.weekday()
        day_type_str = "Weekend" if day_of_week >= 5 else "Weekday"
        
        logger.info(f"Date parsed: day={day}, month={month}, year={year}, dow={day_of_week}, daytype={day_type_str}")
    except ValueError as e:
        logger.error(f"✗ Invalid date format: {str(e)}")
        raise

    # Verify product exists
    if product_name not in rev_nama:
        logger.error(f"✗ Product not found in encoder. Available products: {list(rev_nama.keys())[:5]}...")
        raise ValueError(f"Unknown product: {product_name}")
    
    # Encode features
    nama_code = rev_nama[product_name]
    kategori_str = product_to_kategori.get(product_name, "")
    kategori_code = rev_kategori.get(kategori_str, 0)
    daytype_code = rev_daytype.get(day_type_str, 0)
    
    logger.info(f"Feature encoding:")
    logger.info(f"  - Product: {product_name} → code {nama_code}")
    logger.info(f"  - Category: {kategori_str} → code {kategori_code}")
    logger.info(f"  - DayType: {day_type_str} → code {daytype_code}")
    
    # Create feature vector with column names to prevent UserWarning
    feature_cols = ["day", "month", "year", "DayOfWeek", "Nama_Barang_code", "Kategori_code", "DayType_code"]
    X = pd.DataFrame([[day, month, year, day_of_week, nama_code, kategori_code, daytype_code]], columns=feature_cols)
    logger.info(f"Input features: [day={day}, month={month}, year={year}, dow={day_of_week}, nama={nama_code}, kategori={kategori_code}, daytype={daytype_code}]")
    
    # Make prediction
    try:
        y_pred = model.predict(X)
        logger.info(f"Raw model output: {y_pred[0]}")
    except Exception as e:
        logger.error(f"✗ Model prediction failed: {str(e)}")
        raise

    # Post-process
    predicted_qty = int(round(float(y_pred[0])))
    if predicted_qty < 0:
        logger.info(f"Negative prediction {y_pred[0]} clipped to 0")
        predicted_qty = 0
    
    logger.info(f"Final predicted_qty: {predicted_qty}")
    logger.info(f"=== PREDICTION END ===\n")

    return {
        "predicted_qty": predicted_qty,
    }
