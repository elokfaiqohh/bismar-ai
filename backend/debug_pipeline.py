"""
Comprehensive debugging script to trace the entire prediction pipeline.
Run this to validate predictions and identify issues.

Usage:
    python debug_pipeline.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from ml_model import predict_product_sales as ml_predict, _load_product_model
import models
import crud


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def debug_data_quality(db):
    """Debug: Check data quality and availability."""
    print_section("1. DATA QUALITY CHECK")
    
    # Count records
    total_sales = db.query(models.Sales).count()
    print(f"✓ Total sales records: {total_sales}")
    
    if total_sales == 0:
        print("✗ ERROR: No sales data in database!")
        return False
    
    # Check products
    products = crud.get_products(db=db)
    print(f"✓ Unique products: {len(products)}")
    if len(products) > 0:
        print(f"  Sample products: {[p['nama_barang'] for p in products[:5]]}")
    
    # Check pricing data
    df = pd.read_sql("SELECT * FROM sales LIMIT 10", db.get_bind())
    print(f"\n✓ Database schema columns:")
    for col in df.columns:
        print(f"  - {col}")
    
    # Check for pricing columns
    pricing_cols = ['harga_satuan', 'total_penjualan', 'diskon', 'penjualan_bersih']
    print(f"\n✓ Pricing columns check:")
    for col in pricing_cols:
        if col in df.columns:
            non_null = df[col].notna().sum()
            non_zero = (df[col] > 0).sum()
            print(f"  - {col}: {non_null} non-null, {non_zero} non-zero values")
        else:
            print(f"  - {col}: MISSING ✗")
    
    # Check for null values
    print(f"\n✓ Null values check:")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            print(f"  - {col}: {count} nulls")
    
    return True


def debug_model_loading(db):
    """Debug: Check if model loads correctly."""
    print_section("2. MODEL LOADING CHECK")
    
    try:
        model, rev_nama, rev_kategori, rev_daytype, product_to_kategori = _load_product_model()
        print(f"✓ Model loaded successfully")
        print(f"  - Products in model: {len(rev_nama)}")
        print(f"  - Categories in model: {len(rev_kategori)}")
        print(f"  - Day types in model: {len(rev_daytype)}")
        print(f"  - Product-to-category mappings: {len(product_to_kategori)}")
        
        # Show sample products
        print(f"\n✓ Sample products in model:")
        for i, (code, name) in enumerate(list(rev_nama.items())[:5]):
            cat = product_to_kategori.get(name, 'N/A')
            print(f"  {i+1}. {name} (code={code}, category={cat})")
        
        return True, model, rev_nama, rev_kategori, rev_daytype, product_to_kategori
    except Exception as e:
        print(f"✗ Model loading failed: {str(e)}")
        return False, None, None, None, None, None


def debug_feature_encoding(product_name, rev_nama, rev_kategori, rev_daytype, product_to_kategori):
    """Debug: Check feature encoding for a product."""
    print_section(f"3. FEATURE ENCODING CHECK - Product: {product_name}")
    
    # Check product in mapping
    if product_name in rev_nama:
        nama_code = rev_nama[product_name]
        print(f"✓ Product found in mapping: {product_name} → code {nama_code}")
    else:
        print(f"✗ Product NOT in mapping: {product_name}")
        print(f"  Available products: {list(rev_nama.keys())[:10]}")
        return False
    
    # Check category
    kategori_str = product_to_kategori.get(product_name, "")
    if kategori_str:
        kategori_code = rev_kategori.get(kategori_str, 0)
        print(f"✓ Category found: {kategori_str} → code {kategori_code}")
    else:
        print(f"⚠ Category not found for product")
        kategori_code = 0
    
    # Check day type
    day_type_str = "Weekday"
    daytype_code = rev_daytype.get(day_type_str, 0)
    print(f"✓ Day type: {day_type_str} → code {daytype_code}")
    
    # Create sample features
    test_date = datetime.now()
    X = [[test_date.day, test_date.month, test_date.year, test_date.weekday(), 
          nama_code, kategori_code, daytype_code]]
    print(f"\n✓ Sample feature vector for today:")
    print(f"  X = {X[0]}")
    print(f"     (day={test_date.day}, month={test_date.month}, year={test_date.year}, "
          f"dow={test_date.weekday()}, nama={nama_code}, kategori={kategori_code}, daytype={daytype_code})")
    
    return True


def debug_prediction(db, product_name, test_date=None):
    """Debug: Test actual prediction."""
    print_section(f"4. PREDICTION TEST - Product: {product_name}")
    
    if test_date is None:
        test_date = datetime.now() + timedelta(days=1)
    
    date_str = test_date.strftime('%Y-%m-%d')
    print(f"Test date: {date_str}\n")
    
    try:
        result = ml_predict(date_str=date_str, product_name=product_name)
        predicted_qty = result['predicted_qty']
        print(f"✓ Prediction successful!")
        print(f"  - Predicted Qty: {predicted_qty}")
        
        # Check revenue calculation
        sales_with_price = db.query(models.Sales).filter(
            models.Sales.nama_barang == product_name,
            models.Sales.harga_satuan > 0
        ).first()
        
        if sales_with_price and sales_with_price.harga_satuan:
            price = float(sales_with_price.harga_satuan)
            estimated_revenue = predicted_qty * price
            print(f"  - Unit price: Rp {price:,.0f}")
            print(f"  - Estimated revenue: Rp {estimated_revenue:,.0f}")
        else:
            print(f"  - ⚠ No price data for product")
            print(f"  - Estimated revenue: Cannot calculate")
        
        return True
        
    except Exception as e:
        print(f"✗ Prediction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def debug_database_counts(db):
    """Debug: Show database statistics."""
    print_section("5. DATABASE STATISTICS")
    
    total_sales = db.query(models.Sales).count()
    products_count = len(crud.get_products(db=db))
    
    print(f"Total sales records: {total_sales}")
    print(f"Unique products: {products_count}")
    
    # Show first few records
    print(f"\n✓ First 5 sales records:")
    records = db.query(models.Sales).limit(5).all()
    for i, r in enumerate(records, 1):
        print(f"  {i}. {r.tanggal.strftime('%Y-%m-%d')} | {r.nama_barang} | Qty: {r.kuantitas} | Price: {r.harga_satuan}")


def main():
    """Run comprehensive debugging."""
    print("\n" + "="*80)
    print("  COMPREHENSIVE PREDICTION PIPELINE DEBUGGING")
    print("="*80)
    
    # Initialize database
    db = SessionLocal()
    
    try:
        # Run diagnostics
        if not debug_data_quality(db):
            return
        
        debug_database_counts(db)
        
        success, model, rev_nama, rev_kategori, rev_daytype, product_to_kategori = debug_model_loading(db)
        if not success or model is None:
            return
        
        # Test with first available product
        products = crud.get_products(db=db)
        if len(products) > 0:
            test_product = products[0]['nama_barang']
            print(f"\nUsing test product: {test_product}")
            
            debug_feature_encoding(test_product, rev_nama, rev_kategori, rev_daytype, product_to_kategori)
            debug_prediction(db, test_product)
        
        # Final summary
        print_section("DIAGNOSIS SUMMARY")
        print("✓ All checks completed. If all tests passed, the pipeline should work correctly.")
        print("\nIf predictions are still 0 or NaN:")
        print("1. Check model training data quality")
        print("2. Verify all products from training exist in test data")
        print("3. Ensure database was reseeded with new schema")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
