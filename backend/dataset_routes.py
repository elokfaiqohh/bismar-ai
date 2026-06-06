import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session

try:
    from . import database, models, schemas, populate_prices, seed, ml_model
    from .train_product_model import train_and_save_model
except ImportError:
    import database, models, schemas, populate_prices, seed, ml_model
    from train_product_model import train_and_save_model

router = APIRouter(prefix="/api", tags=["dataset"])
logger = logging.getLogger("dataset_routes")

# Project directories setup
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
MASTER_SALES_CSV = DATASET_DIR / "master_sales.csv"
UPLOADS_DIR = DATASET_DIR / "uploads"
BACKUPS_DIR = DATASET_DIR / "backups"
TEMP_DIR = DATASET_DIR / "temp_uploads"
METADATA_FILE = DATASET_DIR / "metadata.json"
MODEL_PATH = Path(__file__).resolve().parent / "model_product_sales.pkl"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Strict Schema definition
EXPECTED_COLUMNS = [
    'Tanggal', 'Nama_Barang', 'Tipe_Transaksi', 'Kuantitas', 'Satuan',
    'DayOfWeek', 'NamaHari', 'DayType', 'TxOrder', 'TotalPerDay',
    'WaktuRatio', 'Waktu', 'Kategori'
]


def read_metadata():
    if not METADATA_FILE.exists():
        return {"uploads": [], "backups": []}
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading metadata: {e}")
        return {"uploads": [], "backups": []}


def write_metadata(data):
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing metadata: {e}")


def sync_database_from_csv(db: Session, csv_path: Path):
    """Fully truncate and reseed database from master_sales.csv and populate prices."""
    try:
        logger.info(f"Truncating Sales table...")
        db.query(models.Sales).delete()
        db.commit()

        logger.info(f"Seeding Sales table from {csv_path.name}...")
        seed.seed_sales_from_csv(db, csv_path, force=True)

        logger.info(f"Populating prices...")
        pricing_path = DATASET_DIR / "Data2.csv"
        populate_prices.populate_prices_from_csv(pricing_path)
        logger.info("Database sync complete.")
    except Exception as e:
        logger.error(f"Database sync failed: {e}")
        db.rollback()
        raise


def insert_new_sales_records(db: Session, df: pd.DataFrame):
    """Compute and insert only new (non-duplicate) sales records into the database."""
    if df.empty:
        return

    # Load average prices from DB
    avg_prices_query = db.query(
        models.Sales.nama_barang, 
        func.avg(models.Sales.harga_satuan)
    ).filter(models.Sales.harga_satuan > 0).group_by(models.Sales.nama_barang).all()
    avg_prices = {r[0]: float(r[1]) for r in avg_prices_query}

    for _, row in df.iterrows():
        # Parse tanggal
        tanggal_str = str(row['Tanggal'])
        try:
            tanggal_dt = datetime.fromisoformat(tanggal_str)
        except ValueError:
            try:
                tanggal_dt = pd.to_datetime(tanggal_str).to_pydatetime()
            except Exception:
                tanggal_dt = datetime.now()

        # Calculate price fallback
        prod_name = str(row['Nama_Barang'])
        category = str(row['Kategori'])
        if prod_name in avg_prices:
            price = avg_prices[prod_name]
        else:
            price = populate_prices.get_fallback_price(category)

        total_penjualan = float(row.get('Kuantitas', 0) or 0) * price

        sale = models.Sales(
            tanggal=tanggal_dt,
            nama_barang=prod_name,
            tipe_transaksi=str(row.get('Tipe_Transaksi', 'Faktur Penjualan')),
            kuantitas=int(row.get('Kuantitas', 0) or 0),
            satuan=str(row.get('Satuan', 'UNIT')),
            day_of_week=int(row.get('DayOfWeek', 0) or 0),
            nama_hari=str(row.get('NamaHari', '')),
            day_type=str(row.get('DayType', 'Weekday')),
            tx_order=int(row.get('TxOrder', 0) or 0),
            total_per_day=int(row.get('TotalPerDay', 0) or 0),
            waktu_ratio=float(row.get('WaktuRatio', 0.0) or 0.0),
            waktu=str(row.get('Waktu', 'Pagi')),
            kategori=category,
            harga_satuan=price,
            total_penjualan=total_penjualan,
            diskon=0.0,
            penjualan_bersih=total_penjualan,
        )
        db.add(sale)
    
    db.commit()


@router.post("/dataset/upload")
def upload_dataset(file: UploadFile = File(...)):
    """Validate uploaded CSV file strictly and save to temp_uploads, returning preview stats."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    # Generate upload ID
    upload_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_path = TEMP_DIR / f"{upload_id}.csv"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read dataset
        df = pd.read_csv(temp_path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {str(e)}")

    # Strict Validation Check
    errors = []

    # 1. Non-empty check
    if df.empty:
        temp_path.unlink()
        raise HTTPException(status_code=400, detail="Uploaded file is empty (contains no data rows).")

    # 2. Columns existence, naming, and order check
    actual_columns = list(df.columns)
    if actual_columns != EXPECTED_COLUMNS:
        # Check details
        if len(actual_columns) != len(EXPECTED_COLUMNS):
            errors.append(f"Column count mismatch: expected {len(EXPECTED_COLUMNS)}, got {len(actual_columns)}.")
        else:
            for idx, (act, exp) in enumerate(zip(actual_columns, EXPECTED_COLUMNS)):
                if act != exp:
                    errors.append(f"Column mismatch at index {idx}: expected '{exp}', got '{act}'.")
        
        temp_path.unlink()
        raise HTTPException(status_code=400, detail={"errors": errors, "message": "Strict column schema validation failed."})

    # 3. Data types validation
    # Tanggal check
    try:
        pd.to_datetime(df['Tanggal'], errors='raise')
    except Exception:
        errors.append("Invalid dates found in 'Tanggal' column. Must be YYYY-MM-DD or datetime format.")

    # Integer types check
    int_cols = ['Kuantitas', 'DayOfWeek', 'TxOrder', 'TotalPerDay']
    for col in int_cols:
        if not pd.api.types.is_integer_dtype(df[col]) and not pd.to_numeric(df[col], errors='coerce').notnull().all():
            errors.append(f"Column '{col}' must contain only integer numbers.")

    # Float types check
    if not pd.api.types.is_float_dtype(df['WaktuRatio']) and not pd.to_numeric(df['WaktuRatio'], errors='coerce').notnull().all():
        errors.append("Column 'WaktuRatio' must contain only numeric decimal values.")

    if errors:
        temp_path.unlink()
        raise HTTPException(status_code=400, detail={"errors": errors, "message": "Strict data type validation failed."})

    # Calculate previews stats
    total_rows = len(df)
    total_products = int(df['Nama_Barang'].nunique())
    
    # Parse dates to get range
    parsed_dates = pd.to_datetime(df['Tanggal'])
    date_start = parsed_dates.min().strftime('%Y-%m-%d')
    date_end = parsed_dates.max().strftime('%Y-%m-%d')
    
    # Missing values
    missing_values = df.isnull().sum().to_dict()
    
    # Duplicates in file against master_sales.csv
    duplicate_rows = 0
    if MASTER_SALES_CSV.exists():
        try:
            master_df = pd.read_csv(MASTER_SALES_CSV)
            # Find duplicate rows
            merged = master_df.merge(df, how='inner', on=EXPECTED_COLUMNS)
            duplicate_rows = len(merged)
        except Exception:
            pass

    # First 5 sample rows
    sample_rows = df.head(5).fillna("").to_dict(orient="records")

    return {
        "upload_id": upload_id,
        "filename": file.filename,
        "preview": {
            "total_rows": total_rows,
            "total_products": total_products,
            "date_range": {"start": date_start, "end": date_end},
            "missing_values": missing_values,
            "duplicate_rows": duplicate_rows,
            "sample_rows": sample_rows
        }
    }


@router.post("/dataset/import")
def import_dataset(request: schemas.DatasetImportRequest, db: Session = Depends(database.get_db)):
    """Execute either Append or Replace mode import for the validated temporary CSV file."""
    temp_file = TEMP_DIR / f"{request.upload_id}.csv"
    if not temp_file.exists():
        raise HTTPException(status_code=404, detail="Upload file not found or expired. Please upload the file again.")

    if request.mode not in ["APPEND", "REPLACE"]:
        raise HTTPException(status_code=400, detail="Invalid import mode. Must be APPEND or REPLACE.")

    try:
        new_df = pd.read_csv(temp_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse uploaded CSV: {e}")

    metadata = read_metadata()
    upload_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    upload_save_path = UPLOADS_DIR / upload_filename

    # Save copy to uploads
    shutil.copy(temp_file, upload_save_path)

    # Initialize master if missing
    if not MASTER_SALES_CSV.exists():
        # Copy original if master doesn't exist yet
        original_csv = DATASET_DIR / "clean_data_bismar_penjualan.csv"
        if original_csv.exists():
            shutil.copy(original_csv, MASTER_SALES_CSV)
        else:
            # Create empty header file
            pd.DataFrame(columns=EXPECTED_COLUMNS).to_csv(MASTER_SALES_CSV, index=False)

    old_master_df = pd.read_csv(MASTER_SALES_CSV)
    
    total_rows = len(new_df)
    imported_rows = 0
    duplicate_rows = 0
    backup_filename = None

    if request.mode == "APPEND":
        # Incremental Sync Logic
        new_df_cleaned = new_df.drop_duplicates(keep='first')
        
        # Merge outer to identify new unique records
        merged = old_master_df.merge(new_df_cleaned, on=EXPECTED_COLUMNS, how='outer', indicator=True)
        new_records = merged[merged['_merge'] == 'right_only'].drop(columns=['_merge'])
        
        duplicate_rows = total_rows - len(new_records)
        imported_rows = len(new_records)

        if imported_rows > 0:
            # Concatenate master with new rows
            updated_master_df = pd.concat([old_master_df, new_records], ignore_index=True)
            updated_master_df.to_csv(MASTER_SALES_CSV, index=False)
            
            # Incremental sync inside DB: insert only new_records
            insert_new_sales_records(db, new_records)
            
        logger.info(f"APPEND COMPLETE: {imported_rows} imported, {duplicate_rows} skipped duplicates.")

    elif request.mode == "REPLACE":
        # Replace Logic: require backup first
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_filename = f"{backup_id}.csv"
        backup_path = BACKUPS_DIR / backup_filename
        
        # Backup master
        shutil.copy(MASTER_SALES_CSV, backup_path)
        
        # Overwrite master with uploaded
        new_df.to_csv(MASTER_SALES_CSV, index=False)
        imported_rows = total_rows
        
        # Full DB Reseed and price population
        sync_database_from_csv(db, MASTER_SALES_CSV)

        # Log backup metadata
        metadata["backups"].append({
            "backup_id": backup_id,
            "backup_filename": backup_filename,
            "backup_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source_upload": request.upload_id,
            "row_count": len(old_master_df)
        })
        
        logger.info(f"REPLACE COMPLETE: Backup {backup_filename} created. Database fully reseeded.")

    # Save upload metadata
    metadata["uploads"].append({
        "upload_id": request.upload_id,
        "filename": upload_filename,
        "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "upload_mode": request.mode,
        "total_rows": total_rows,
        "imported_rows": imported_rows,
        "duplicate_rows": duplicate_rows,
        "backup_file": backup_filename,
        "notes": f"Imported successfully via {request.mode} mode."
    })
    write_metadata(metadata)

    # Clear temp file
    temp_file.unlink()

    # Clear ML model cache
    ml_model._cached_product_model = None

    return {
        "status": "success",
        "mode": request.mode,
        "imported_rows": imported_rows,
        "duplicate_rows": duplicate_rows,
        "backup_file": backup_filename
    }


@router.get("/dataset/history")
def get_dataset_history():
    """Return upload and backup logs from dataset/metadata.json."""
    return read_metadata()


@router.get("/dataset/statistics")
def get_dataset_statistics(db: Session = Depends(database.get_db)):
    """Compute and return statistics of dataset/master_sales.csv."""
    if not MASTER_SALES_CSV.exists():
        return {
            "total_records": 0,
            "total_products": 0,
            "date_range": {"start": None, "end": None},
            "total_revenue": 0.0,
            "category_distribution": {}
        }

    try:
        df = pd.read_csv(MASTER_SALES_CSV)
        total_records = len(df)
        total_products = int(df['Nama_Barang'].nunique())
        
        parsed_dates = pd.to_datetime(df['Tanggal'])
        date_start = parsed_dates.min().strftime('%Y-%m-%d') if not parsed_dates.empty else None
        date_end = parsed_dates.max().strftime('%Y-%m-%d') if not parsed_dates.empty else None
        
        # Category distribution
        category_distribution = df['Kategori'].value_counts().to_dict()
        
        # Total Revenue from DB
        total_rev_scalar = db.query(func.sum(models.Sales.penjualan_bersih)).scalar()
        total_revenue = float(total_rev_scalar or 0.0)

        return {
            "total_records": total_records,
            "total_products": total_products,
            "date_range": {"start": date_start, "end": date_end},
            "total_revenue": total_revenue,
            "category_distribution": category_distribution
        }
    except Exception as e:
        logger.error(f"Error computing dataset statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate statistics.")


@router.post("/dataset/restore-latest")
def restore_latest_backup(db: Session = Depends(database.get_db)):
    """Restore dataset and database from the most recent backup."""
    metadata = read_metadata()
    backups = metadata.get("backups", [])
    if not backups:
        raise HTTPException(status_code=400, detail="No backups available to restore.")

    # Get latest backup
    latest_backup = sorted(backups, key=lambda b: b["backup_date"])[-1]
    return restore_backup(latest_backup["backup_id"], db)


@router.post("/dataset/restore/{backup_id}")
def restore_backup(backup_id: str, db: Session = Depends(database.get_db)):
    """Restore dataset and database to target backup ID, creating a backup of current data first."""
    metadata = read_metadata()
    backup_entry = next((b for b in metadata.get("backups", []) if b["backup_id"] == backup_id), None)
    
    if not backup_entry:
        raise HTTPException(status_code=404, detail=f"Backup with ID {backup_id} not found.")

    backup_path = BACKUPS_DIR / backup_entry["backup_filename"]
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup CSV file is missing on disk.")

    try:
        # Create safety backup of current master_sales.csv before overwrite
        safety_backup_id = f"backup_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        safety_filename = f"{safety_backup_id}.csv"
        safety_path = BACKUPS_DIR / safety_filename
        
        old_master_len = 0
        if MASTER_SALES_CSV.exists():
            shutil.copy(MASTER_SALES_CSV, safety_path)
            old_df = pd.read_csv(MASTER_SALES_CSV)
            old_master_len = len(old_df)
            
            # Log safety backup
            metadata["backups"].append({
                "backup_id": safety_backup_id,
                "backup_filename": safety_filename,
                "backup_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "source_upload": "PRE_RESTORE_SAFETY",
                "row_count": old_master_len
            })

        # Overwrite master_sales.csv with target backup
        shutil.copy(backup_path, MASTER_SALES_CSV)

        # Full DB Reseed
        sync_database_from_csv(db, MASTER_SALES_CSV)

        # Log restoration in metadata
        metadata["uploads"].append({
            "upload_id": f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "filename": backup_entry["backup_filename"],
            "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "upload_mode": "RESTORE",
            "total_rows": len(pd.read_csv(MASTER_SALES_CSV)),
            "imported_rows": len(pd.read_csv(MASTER_SALES_CSV)),
            "duplicate_rows": 0,
            "backup_file": safety_filename,
            "notes": f"Restored from backup {backup_id}."
        })
        write_metadata(metadata)

        # Clear ML model cache
        ml_model._cached_product_model = None

        return {
            "status": "success",
            "restored_backup": backup_id,
            "safety_backup_created": safety_backup_id
        }
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")


@router.post("/model/retrain")
def retrain_model(background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    """Trigger manual retraining on dataset/master_sales.csv."""
    if not MASTER_SALES_CSV.exists():
        raise HTTPException(status_code=400, detail="Active dataset (master_sales.csv) does not exist.")

    def run_retraining():
        try:
            logger.info("Starting background model retraining...")
            train_and_save_model(MASTER_SALES_CSV, MODEL_PATH)
            # Clear ML model cache
            ml_model._cached_product_model = None
            logger.info("Background model retraining finished successfully.")
        except Exception as e:
            logger.error(f"Background model retraining failed: {e}")

    background_tasks.add_task(run_retraining)
    return {"status": "started", "message": "Model retraining has been triggered in the background."}
