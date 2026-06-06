"""Populate product pricing from historical data."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models import Sales

def get_fallback_price(category: str) -> float:
    category_prices = {
        'Notebook/Laptop': 8500000.0,
        'Aksesoris/Komponen': 150000.0,
        'Jasa Service': 100000.0,
        'Smartphone': 3500000.0,
        'Printer': 2000000.0,
        'Elektronik Rumah': 1200000.0,
        'Monitor/TV': 1800000.0,
        'Perangkat/Gadget': 2500000.0,
        'Lainnya': 50000.0
    }
    return category_prices.get(category, 100000.0)


def populate_prices_from_csv(pricing_csv_path: Path):
    """Populate pricing columns in database from pricing CSV and fallback rules."""
    print("\n" + "="*80)
    print("POPULATING PRODUCT PRICES FROM CSV & FALLBACKS")
    print("="*80 + "\n")
    
    # Load pricing data
    pricing_df = pd.read_csv(pricing_csv_path)
    print(f"Loaded {len(pricing_df)} pricing records from {pricing_csv_path.name}")
    
    # Calculate average price per product
    avg_prices = pricing_df.groupby('nama_produk')['harga_satuan'].mean().to_dict()
    print(f"Found {len(avg_prices)} unique products with pricing")
    
    # Update database
    db = SessionLocal()
    
    # Get all unique products from database
    products = db.query(Sales.nama_barang).distinct().all()
    print(f"\nFound {len(products)} unique products in database")
    
    updated_count = 0
    not_found = []
    
    for (product_name,) in products:
        # Try to find matching product in pricing data
        if product_name in avg_prices:
            price = avg_prices[product_name]
        else:
            # Fallback based on category
            sale_record = db.query(Sales).filter(Sales.nama_barang == product_name).first()
            category = sale_record.kategori if sale_record else 'Lainnya'
            price = get_fallback_price(category)
            not_found.append(product_name)
            
        # Update all records for this product: harga_satuan, total_penjualan, penjualan_bersih
        count = db.query(Sales).filter(
            Sales.nama_barang == product_name
        ).update({
            Sales.harga_satuan: price,
            Sales.total_penjualan: Sales.kuantitas * price,
            Sales.penjualan_bersih: Sales.kuantitas * price - Sales.diskon
        }, synchronize_session=False)
        
        if count > 0:
            updated_count += count
    
    db.commit()
    db.close()
    
    print(f"\n✓ Updated {updated_count} records with pricing")
    print(f"⚠️  {len(not_found)} products not found in pricing data")
    
    if not_found[:5]:
        print(f"\nSample of unfound products:")
        for p in not_found[:5]:
            print(f"  - {p}")
    
    print("\n" + "="*80 + "\n")


def main():
    dataset_path = Path(__file__).parent.parent / "dataset"
    pricing_csv = dataset_path / "Data2.csv"
    
    if not pricing_csv.exists():
        print(f"❌ Pricing CSV not found: {pricing_csv}")
        return
    
    populate_prices_from_csv(pricing_csv)


if __name__ == "__main__":
    main()
