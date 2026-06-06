import os
from pathlib import Path

import pandas as pd

# Support running from within backend/ directory (as script) and as a package.
try:
    from . import models
except ImportError:  # pragma: no cover
    import models


def seed_sales_from_csv(db, csv_path: str | Path, force: bool = False) -> int:
    """Seed the sales table from a CSV file.

    Args:
        db: DB session.
        csv_path: Path to a CSV file containing sales data.
        force: If True, existing rows are removed before seeding.

    Returns:
        Number of rows inserted.
    """

    # Optionally clear existing data
    if force:
        db.query(models.Sales).delete()
        db.commit()

    # If not forced and data exists, do nothing
    if not force and db.query(models.Sales).first() is not None:
        return 0

    csv_path = Path(csv_path)
    if not csv_path.exists():
        return

    df = pd.read_csv(csv_path)

    # Normalize column names (case & whitespace) and ensure expected columns exist
    df.columns = [c.strip().lower() for c in df.columns]
    expected = {
        "tanggal",
        "nama_barang",
        "tipe_transaksi",
        "kuantitas",
        "satuan",
        "dayofweek",
        "namahari",
        "daytype",
        "txorder",
        "totalperday",
        "wakturatio",
        "waktu",
        "kategori",
    }
    if not expected.issubset(set(df.columns)):
        return

    # Parse dates
    df["tanggal"] = pd.to_datetime(df["tanggal"], dayfirst=False, errors="coerce")
    df = df.dropna(subset=["tanggal"])

    inserted = 0
    for row in df.to_dict(orient="records"):
        waktu_ratio_raw = str(row.get("wakturatio", 0)).replace(",", ".")
        waktu_ratio = float(waktu_ratio_raw) if waktu_ratio_raw.replace('.', '', 1).isdigit() else 0.0
        
        # Parse pricing columns (optional, may not exist in all CSV files)
        harga_satuan = 0.0
        total_penjualan = 0.0
        diskon = 0.0
        penjualan_bersih = 0.0
        
        if "harga_satuan" in df.columns:
            harga_str = str(row.get("harga_satuan", 0)).replace(",", ".")
            harga_satuan = float(harga_str) if harga_str.replace('.', '', 1).replace('-', '', 1).isdigit() else 0.0
        
        if "total_penjualan" in df.columns:
            total_str = str(row.get("total_penjualan", 0)).replace(",", ".")
            total_penjualan = float(total_str) if total_str.replace('.', '', 1).replace('-', '', 1).isdigit() else 0.0
        
        if "diskon" in df.columns:
            diskon_str = str(row.get("diskon", 0)).replace(",", ".")
            diskon = float(diskon_str) if diskon_str.replace('.', '', 1).replace('-', '', 1).isdigit() else 0.0
        
        if "penjualan_bersih" in df.columns:
            bersih_str = str(row.get("penjualan_bersih", 0)).replace(",", ".")
            penjualan_bersih = float(bersih_str) if bersih_str.replace('.', '', 1).replace('-', '', 1).isdigit() else 0.0
        
        sale = models.Sales(
            tanggal=row["tanggal"].to_pydatetime() if hasattr(row["tanggal"], "to_pydatetime") else row["tanggal"],
            nama_barang=str(row.get("nama_barang", "")),
            tipe_transaksi=str(row.get("tipe_transaksi", "")),
            kuantitas=int(row.get("kuantitas", 0) or 0),
            satuan=str(row.get("satuan", "")),
            day_of_week=int(row.get("dayofweek", 0) or 0),
            nama_hari=str(row.get("namahari", "")),
            day_type=str(row.get("daytype", "")),
            tx_order=int(row.get("txorder", 0) or 0),
            total_per_day=int(row.get("totalperday", 0) or 0),
            waktu_ratio=waktu_ratio,
            waktu=str(row.get("waktu", "")),
            kategori=str(row.get("kategori", "")),
            harga_satuan=harga_satuan,
            total_penjualan=total_penjualan,
            diskon=diskon,
            penjualan_bersih=penjualan_bersih,
        )
        db.add(sale)
        inserted += 1

    db.commit()
    return inserted
