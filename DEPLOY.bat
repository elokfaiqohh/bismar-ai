@echo off
REM DEPLOYMENT GUIDE: Sales Forecasting Application Fix (Windows)
REM 
REM This script helps you deploy the fixes and verify they work correctly.
REM Run this as administrator for best results.

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   SALES FORECASTING FIX DEPLOYMENT
echo ==========================================
echo.

cd /d "%~dp0backend"
set BACKEND_DIR=%cd%

echo Folder: %BACKEND_DIR%
echo.

REM Step 1: Delete old database
echo Step 1: Resetting database...
if exist "sales.db" (
    echo   Deleting old database: %BACKEND_DIR%\sales.db
    del /f /q "sales.db"
    echo   OK - Old database deleted
) else (
    echo   No existing database found
)

echo.
echo Step 2: Verify Python...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   ERROR: Python not found. Please install Python 3.8+
    exit /b 1
)

python --version
if %errorlevel% neq 0 (
    echo   ERROR: Python check failed
    exit /b 1
)
echo   OK - Python found

echo.
echo Step 3: Checking dependencies...

python -c "import fastapi" >nul 2>nul
if %errorlevel% neq 0 (
    echo   Installing fastapi...
    python -m pip install fastapi -q
)
echo   OK - fastapi

python -c "import sqlalchemy" >nul 2>nul
if %errorlevel% neq 0 (
    echo   Installing sqlalchemy...
    python -m pip install sqlalchemy -q
)
echo   OK - sqlalchemy

python -c "import pandas" >nul 2>nul
if %errorlevel% neq 0 (
    echo   Installing pandas...
    python -m pip install pandas -q
)
echo   OK - pandas

python -c "import sklearn" >nul 2>nul
if %errorlevel% neq 0 (
    echo   Installing scikit-learn...
    python -m pip install scikit-learn -q
)
echo   OK - scikit-learn

python -c "import joblib" >nul 2>nul
if %errorlevel% neq 0 (
    echo   Installing joblib...
    python -m pip install joblib -q
)
echo   OK - joblib

echo.
echo Step 4: Testing database schema...

python << 'PYTHON_EOF'
import sys
try:
    from database import engine
    from models import Base, Sales
    
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('sales')]
    
    required_cols = ['harga_satuan', 'total_penjualan', 'diskon', 'penjualan_bersih']
    
    print("Database schema check:")
    all_ok = True
    for col in required_cols:
        if col in columns:
            print(f"  OK - {col}")
        else:
            print(f"  ERROR - {col} MISSING")
            all_ok = False
    
    if all_ok:
        print("\nOK - Database schema is correct!")
        sys.exit(0)
    else:
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF

if %errorlevel% neq 0 (
    echo   ERROR - Database schema check failed
    exit /b 1
)

echo.
echo Step 5: Testing data import...

python << 'PYTHON_EOF'
import sys
from pathlib import Path

try:
    from database import SessionLocal
    from seed import seed_sales_from_csv
    from crud import get_sales, get_products
    
    db = SessionLocal()
    
    csv_path = Path(__file__).parent.parent.parent / "dataset" / "clean_data_bismar_penjualan.csv"
    print(f"Seeding from: {csv_path}")
    
    if csv_path.exists():
        inserted = seed_sales_from_csv(db, csv_path, force=True)
        print(f"OK - Imported {inserted} sales records")
        
        sales_count = len(get_sales(db))
        products_count = len(get_products(db))
        print(f"OK - Total sales: {sales_count}")
        print(f"OK - Unique products: {products_count}")
        
        from models import Sales as SalesModel
        sales_with_price = db.query(SalesModel).filter(
            SalesModel.harga_satuan > 0
        ).count()
        print(f"OK - Records with pricing: {sales_with_price}")
        
        if sales_with_price > 0:
            print("OK - Pricing data successfully imported!")
        else:
            print("WARNING - No pricing data found in CSV")
    else:
        print(f"WARNING - Dataset not found: {csv_path}")
    
    db.close()
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF

if %errorlevel% neq 0 (
    echo   ERROR - Data import test failed
    exit /b 1
)

echo.
echo ==========================================
echo   OK - DEPLOYMENT READY
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Start the backend server:
echo    cd backend
echo    python -m uvicorn app:app --reload
echo.
echo 2. In another terminal, run the debug script:
echo    cd backend
echo    python debug_pipeline.py
echo.
echo 3. Test the prediction endpoint with curl or Postman:
echo    POST http://localhost:8000/predict-product
echo    Headers: Content-Type: application/json
echo    Body: {"date": "2026-06-10", "product_id": "PRODUCT_NAME"}
echo.
echo 4. Open frontend and verify predictions show correct Qty and Revenue
echo.
echo ==========================================
echo.

pause
