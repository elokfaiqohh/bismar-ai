"""Comprehensive debugging script to trace the entire prediction pipeline."""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import joblib

# Support imports from both script and package context
sys.path.insert(0, str(Path(__file__).parent))

import ml_model
from database import SessionLocal, engine
from models import Sales, Base

def debug_database():
    """Check database structure and data."""
    print("\n" + "="*80)
    print("1. DATABASE ANALYSIS")
    print("="*80)
    
    db = SessionLocal()
    
    # Check data count
    sales_count = db.query(Sales).count()
    print(f"Total sales records: {sales_count}")
    
    if sales_count == 0:
        print("⚠️  WARNING: Database is empty! No sales data available.")
        return
    
    # Get sample data
    sample = db.query(Sales).limit(3).all()
    print(f"\nSample sales records:")
    for s in sample:
        print(f"  - Date: {s.tanggal}, Product: {s.nama_barang}, Qty: {s.kuantitas}, Price: {s.harga_satuan}, Category: {s.kategori}")
    
    # Get unique products
    products = db.query(Sales.nama_barang).distinct().all()
    print(f"\nUnique products ({len(products)}):")
    for i, (prod,) in enumerate(products[:5]):
        count = db.query(Sales).filter(Sales.nama_barang == prod).count()
        print(f"  {i+1}. {prod} ({count} records)")
    
    db.close()


def debug_model_loading():
    """Check if model file exists and can be loaded."""
    print("\n" + "="*80)
    print("2. MODEL LOADING ANALYSIS")
    print("="*80)
    
    model_path = Path(__file__).parent / "model_product_sales.pkl"
    
    if not model_path.exists():
        print(f"❌ ERROR: Model file not found at {model_path}")
        print("   Run: python train_product_model.py")
        return None
    
    print(f"✓ Model file found: {model_path}")
    
    try:
        data = joblib.load(model_path)
        print(f"✓ Model loaded successfully")
        
        model = data.get("model")
        mapping_nama = data.get("nama_barang_mapping")
        mapping_kategori = data.get("kategori_mapping")
        mapping_daytype = data.get("daytype_mapping")
        product_to_kategori = data.get("product_to_kategori")
        
        print(f"\nModel components:")
        print(f"  - Model type: {type(model).__name__}")
        print(f"  - Products in mapping: {len(mapping_nama)}")
        print(f"  - Categories in mapping: {len(mapping_kategori)}")
        print(f"  - Day types in mapping: {len(mapping_daytype)}")
        print(f"  - Product-to-category mappings: {len(product_to_kategori)}")
        
        print(f"\nProduct mappings (first 5):")
        for i, (code, name) in enumerate(list(mapping_nama.items())[:5]):
            print(f"  {code} → '{name}'")
        
        print(f"\nCategory mappings:")
        for code, name in mapping_kategori.items():
            print(f"  {code} → '{name}'")
        
        print(f"\nDay type mappings:")
        for code, name in mapping_daytype.items():
            print(f"  {code} → '{name}'")
        
        return data
    
    except Exception as e:
        print(f"❌ ERROR loading model: {str(e)}")
        return None


def debug_product_encoding(data: dict):
    """Check if specific products exist in encoder."""
    if data is None:
        return
    
    print("\n" + "="*80)
    print("3. PRODUCT ENCODING ANALYSIS")
    print("="*80)
    
    mapping_nama = data.get("nama_barang_mapping", {})
    rev_nama = {v: k for k, v in mapping_nama.items()}
    
    db = SessionLocal()
    products = db.query(Sales.nama_barang).distinct().limit(5).all()
    
    print(f"Checking {len(products)} products in training data:")
    for (prod,) in products:
        if prod in rev_nama:
            code = rev_nama[prod]
            print(f"  ✓ '{prod}' → code {code}")
        else:
            print(f"  ❌ '{prod}' NOT in encoder mapping")
    
    db.close()


def debug_feature_engineering():
    """Test feature engineering for a specific date and product."""
    print("\n" + "="*80)
    print("4. FEATURE ENGINEERING ANALYSIS")
    print("="*80)
    
    # Test date: tomorrow
    test_date_str = "2026-06-07"  # Tomorrow
    test_product_name = None
    
    # Get first available product
    db = SessionLocal()
    first_product = db.query(Sales.nama_barang).distinct().first()
    if first_product:
        test_product_name = first_product[0]
    db.close()
    
    if not test_product_name:
        print("❌ No products in database")
        return
    
    print(f"Test date: {test_date_str}")
    print(f"Test product: {test_product_name}")
    
    try:
        dt = datetime.fromisoformat(test_date_str)
        day = dt.day
        month = dt.month
        year = dt.year
        day_of_week = dt.weekday()
        day_type_str = "Weekend" if day_of_week >= 5 else "Weekday"
        
        print(f"\nExtracted date features:")
        print(f"  - Day: {day}")
        print(f"  - Month: {month}")
        print(f"  - Year: {year}")
        print(f"  - Day of week: {day_of_week} (0=Mon, 5=Sat, 6=Sun)")
        print(f"  - Day type: {day_type_str}")
        
    except ValueError as e:
        print(f"❌ Date parsing error: {str(e)}")


def debug_prediction(data: dict):
    """Perform a full prediction with detailed logging."""
    if data is None:
        return
    
    print("\n" + "="*80)
    print("5. FULL PREDICTION TRACE")
    print("="*80)
    
    # Get test data
    db = SessionLocal()
    first_product = db.query(Sales.nama_barang).distinct().first()
    if not first_product:
        print("❌ No products in database")
        return
    
    test_product_name = first_product[0]
    test_date_str = "2026-06-07"
    
    print(f"Testing prediction for:")
    print(f"  Product: {test_product_name}")
    print(f"  Date: {test_date_str}")
    
    db.close()
    
    try:
        result = ml_model.predict_product_sales(test_date_str, test_product_name)
        print(f"\n✓ Prediction successful:")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"\n❌ Prediction failed:")
        print(f"  Error: {str(e)}")
        import traceback
        traceback.print_exc()


def debug_revenue_calculation(data: dict):
    """Debug revenue calculation logic."""
    print("\n" + "="*80)
    print("6. REVENUE CALCULATION ANALYSIS")
    print("="*80)
    
    db = SessionLocal()
    
    # Get sample product with price
    product_with_price = db.query(Sales).filter(
        Sales.harga_satuan > 0
    ).first()
    
    if not product_with_price:
        print("⚠️  WARNING: No products with prices found in database")
        db.close()
        return
    
    product_name = product_with_price.nama_barang
    avg_price = product_with_price.harga_satuan
    
    print(f"Sample product: {product_name}")
    print(f"Unit price from database: {avg_price}")
    
    # Get a prediction for this product
    try:
        result = ml_model.predict_product_sales("2026-06-07", product_name)
        predicted_qty = result["predicted_qty"]
        
        print(f"\nPredicted quantity: {predicted_qty}")
        print(f"Unit price: {avg_price}")
        
        estimated_revenue = predicted_qty * avg_price
        
        print(f"\nRevenue calculation:")
        print(f"  Revenue = Qty × Price")
        print(f"  Revenue = {predicted_qty} × {avg_price}")
        print(f"  Revenue = {estimated_revenue}")
        
        if estimated_revenue == 0 and predicted_qty == 0:
            print(f"\n⚠️  WARNING: Revenue is 0 because predicted_qty is 0!")
        elif pd.isna(estimated_revenue):
            print(f"\n⚠️  WARNING: Revenue is NaN!")
        else:
            print(f"\n✓ Revenue calculation looks correct")
    
    except Exception as e:
        print(f"❌ Error during revenue calculation: {str(e)}")
    
    db.close()


def debug_training_data():
    """Check if training data matches prediction features."""
    print("\n" + "="*80)
    print("7. TRAINING DATA VALIDATION")
    print("="*80)
    
    dataset_path = Path(__file__).parent.parent / "dataset" / "clean_data_bismar_penjualan.csv"
    
    if not dataset_path.exists():
        print(f"⚠️  Dataset not found: {dataset_path}")
        return
    
    try:
        df = pd.read_csv(dataset_path)
        print(f"Dataset shape: {df.shape} (rows × columns)")
        
        print(f"\nDataset columns:")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nDataset info:")
        print(f"  - Total records: {len(df)}")
        print(f"  - Date range: {df.get('Tanggal', df.get('tanggal', ['?'])).iloc[0]}")
        
        # Check for required columns
        required = ["Tanggal", "Nama_Barang", "Kategori", "DayType", "Kuantitas", "DayOfWeek"]
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            print(f"\n⚠️  Missing columns: {missing}")
        else:
            print(f"\n✓ All required columns present")
        
        # Check data types
        print(f"\nKey column data types:")
        for col in ["Tanggal", "Kuantitas", "DayOfWeek"]:
            if col in df.columns:
                print(f"  - {col}: {df[col].dtype}")
    
    except Exception as e:
        print(f"❌ Error reading dataset: {str(e)}")


def main():
    """Run all debugging checks."""
    print("\n" + "="*80)
    print("COMPREHENSIVE PREDICTION PIPELINE DEBUG")
    print("="*80)
    
    debug_database()
    data = debug_model_loading()
    debug_product_encoding(data)
    debug_feature_engineering()
    debug_prediction(data)
    debug_revenue_calculation(data)
    debug_training_data()
    
    print("\n" + "="*80)
    print("DEBUG COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
