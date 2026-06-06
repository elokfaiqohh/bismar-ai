#!/bin/bash
# DEPLOYMENT GUIDE: Sales Forecasting Application Fix
# 
# This script helps you deploy the fixes and verify they work correctly.
# Run this after pulling the code changes.

set -e  # Exit on first error

echo "=========================================="
echo "  SALES FORECASTING FIX DEPLOYMENT"
echo "=========================================="

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/backend" && pwd)"

echo ""
echo "📁 Working directory: $BACKEND_DIR"
echo ""

# Step 1: Delete old database
echo "Step 1: Resetting database..."
if [ -f "$BACKEND_DIR/sales.db" ]; then
    echo "  ⚠️  Deleting old database: $BACKEND_DIR/sales.db"
    rm -f "$BACKEND_DIR/sales.db"
    echo "  ✓ Old database deleted"
else
    echo "  ℹ️  No existing database found"
fi

echo ""
echo "Step 2: Verify Python environment..."
cd "$BACKEND_DIR"

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "  ✗ Python not found. Please install Python 3.8+"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "  ✓ Python found: $PYTHON_CMD"

# Check dependencies
echo ""
echo "Step 3: Checking dependencies..."
required_packages=("fastapi" "sqlalchemy" "pandas" "scikit-learn" "joblib")

for package in "${required_packages[@]}"; do
    if $PYTHON_CMD -c "import $package" 2>/dev/null; then
        echo "  ✓ $package installed"
    else
        echo "  ✗ $package NOT installed - installing..."
        $PYTHON_CMD -m pip install $package -q
    fi
done

echo ""
echo "Step 4: Testing database schema..."
$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path

try:
    from database import engine
    from models import Base, Sales
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Check if new columns exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('sales')]
    
    required_cols = ['harga_satuan', 'total_penjualan', 'diskon', 'penjualan_bersih']
    
    print("Database schema check:")
    for col in required_cols:
        if col in columns:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ {col} MISSING")
            sys.exit(1)
    
    print("\n✓ Database schema is correct!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "  ✗ Database schema check failed"
    exit 1
fi

echo ""
echo "Step 5: Testing data import..."
$PYTHON_CMD << 'EOF'
import sys
from pathlib import Path

try:
    from database import SessionLocal
    from seed import seed_sales_from_csv
    from crud import get_sales, get_products
    
    db = SessionLocal()
    
    # Seed data
    csv_path = Path(__file__).parent.parent / "dataset" / "clean_data_bismar_penjualan.csv"
    print(f"Seeding from: {csv_path}")
    
    if csv_path.exists():
        inserted = seed_sales_from_csv(db, csv_path, force=True)
        print(f"✓ Imported {inserted} sales records")
        
        # Verify
        sales_count = len(get_sales(db))
        products_count = len(get_products(db))
        print(f"✓ Total sales: {sales_count}")
        print(f"✓ Unique products: {products_count}")
        
        # Check pricing data
        from models import Sales as SalesModel
        sales_with_price = db.query(SalesModel).filter(
            SalesModel.harga_satuan > 0
        ).count()
        print(f"✓ Records with pricing: {sales_with_price}")
        
        if sales_with_price > 0:
            print("✓ Pricing data successfully imported!")
        else:
            print("⚠️  Warning: No pricing data found in CSV")
    else:
        print(f"⚠️  Dataset not found: {csv_path}")
    
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "  ✗ Data import test failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "  ✓ DEPLOYMENT READY"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend server:"
echo "   cd backend"
echo "   uvicorn app:app --reload"
echo ""
echo "2. In another terminal, run the debug script:"
echo "   cd backend"
echo "   python debug_pipeline.py"
echo ""
echo "3. Test the prediction endpoint:"
echo "   curl -X POST http://localhost:8000/predict-product \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"date\": \"2026-06-10\", \"product_id\": \"PRODUCT_NAME\"}'"
echo ""
echo "4. Open frontend and verify predictions show correct Qty and Revenue"
echo ""
echo "=========================================="
