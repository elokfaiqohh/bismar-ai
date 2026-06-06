"""Script to seed the database and retrain the model."""

import sys
from pathlib import Path

# Support imports
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, engine
import models
import seed
import train_product_model
from logger import get_logger

logger = get_logger(__name__)

def main():
    print("\n" + "="*80)
    print("SEEDING DATABASE AND RETRAINING MODEL")
    print("="*80 + "\n")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Seed sales data
    db = SessionLocal()
    csv_path = Path(__file__).parent.parent / "dataset" / "clean_data_bismar_penjualan.csv"
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"\n📁 Loading dataset from: {csv_path}")
    inserted = seed.seed_sales_from_csv(db, csv_path, force=True)
    print(f"✓ Inserted {inserted} records into database")
    
    db.close()
    
    # Retrain model
    print("\n🤖 Retraining ensemble model...")
    try:
        dataset_path = Path(__file__).parent.parent / "dataset" / "clean_data_bismar_penjualan.csv"
        output_path = Path(__file__).parent / "model_product_sales.pkl"
        train_product_model.train_and_save_model(dataset_path, output_path)
        print("✓ Model retrained and saved")
    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*80)
    print("✓ SEEDING AND RETRAINING COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
