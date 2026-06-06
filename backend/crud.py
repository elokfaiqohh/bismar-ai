from datetime import date, datetime
from typing import Any, Optional
import pandas as pd

from sqlalchemy import func, text
from sqlalchemy.orm import Session

# Support running from within backend/ directory (as script) and as a package.
try:
    from . import models, schemas
except ImportError:  # pragma: no cover
    import models
    import schemas


def create_sales(db: Session, sales: schemas.SalesCreate) -> models.Sales:
    db_sales = models.Sales(
        tanggal=sales.tanggal,
        nama_barang=sales.nama_barang,
        tipe_transaksi=sales.tipe_transaksi,
        kuantitas=sales.kuantitas,
        satuan=sales.satuan,
        day_of_week=sales.day_of_week,
        nama_hari=sales.nama_hari,
        day_type=sales.day_type,
        tx_order=sales.tx_order,
        total_per_day=sales.total_per_day,
        waktu_ratio=sales.waktu_ratio,
        waktu=sales.waktu,
        kategori=sales.kategori,
        harga_satuan=sales.harga_satuan,
        total_penjualan=sales.total_penjualan,
        diskon=sales.diskon,
        penjualan_bersih=sales.penjualan_bersih,
    )
    db.add(db_sales)
    db.commit()
    db.refresh(db_sales)
    return db_sales


def get_sales(db: Session) -> list[models.Sales]:
    return db.query(models.Sales).order_by(models.Sales.tanggal).all()


def get_sales_by_id(db: Session, sales_id: int) -> models.Sales | None:
    return db.query(models.Sales).filter(models.Sales.id == sales_id).first()


def update_sales(db: Session, sales: models.Sales, sales_in: schemas.SalesUpdate) -> models.Sales:
    for field, value in sales_in.dict(exclude_unset=True).items():
        setattr(sales, field, value)
    db.add(sales)
    db.commit()
    db.refresh(sales)
    return sales


def delete_sales(db: Session, sales: models.Sales) -> None:
    db.delete(sales)
    db.commit()


def get_monthly_sales(db: Session) -> list[dict[str, Any]]:
    """Return list of {month: 'YYYY-MM', total_kuantitas: float, penjualan_bersih: float} sorted by month."""
    rows = (
        db.query(models.Sales)
        .order_by(models.Sales.tanggal)
        .all()
    )

    monthly = {}
    for row in rows:
        month_key = row.tanggal.strftime("%Y-%m")
        monthly.setdefault(month_key, {"kuantitas": 0.0, "penjualan_bersih": 0.0})
        monthly[month_key]["kuantitas"] += float(row.kuantitas or 0.0)
        monthly[month_key]["penjualan_bersih"] += float(row.penjualan_bersih or 0.0)

    # Sort by month
    return [
        {
            "month": k,
            "penjualan_bersih": v["penjualan_bersih"],
            "total_kuantitas": v["kuantitas"]
        }
        for k, v in sorted(monthly.items())
    ]


def get_products(db: Session) -> list[dict[str, str]]:
    """Return unique product names available in the sales data."""
    rows = (
        db.query(models.Sales.nama_barang)
        .distinct()
        .order_by(models.Sales.nama_barang)
        .all()
    )
    return [
        {
            "nama_barang": r.nama_barang,
            "product_id": r.nama_barang,
            "nama_produk": r.nama_barang
        }
        for r in rows
    ]


def get_product_by_code(db: Session, kode_produk: str) -> dict[str, str] | None:
    """Return a single product's metadata from sales records."""
    row = (
        db.query(models.Sales.nama_barang)
        .filter(models.Sales.nama_barang == kode_produk)
        .order_by(models.Sales.tanggal.desc())
        .first()
    )
    if not row:
        return None
    return {
        "nama_barang": row.nama_barang,
        "product_id": row.nama_barang,
        "nama_produk": row.nama_barang
    }


def get_last_sale_date_for_product(db: Session, kode_produk: str) -> date | None:
    """Return the date of the most recent sale for a product."""
    last_sale = (
        db.query(func.max(models.Sales.tanggal))
        .filter(models.Sales.nama_barang == kode_produk)
        .scalar()
    )
    return last_sale.date() if last_sale else None


def get_dead_stock_products(db: Session, cutoff_days: int = 60) -> list[dict[str, object]]:
    """Return products that have not sold in the last `cutoff_days` days."""
    today = datetime.today().date()

    rows = (
        db.query(
            models.Sales.nama_barang,
            func.max(models.Sales.tanggal).label("last_sale"),
        )
        .group_by(models.Sales.nama_barang)
        .all()
    )

    dead = []
    for nama_barang, last_sale in rows:
        if last_sale is None:
            continue
        days_without = (today - last_sale.date()).days
        if days_without >= cutoff_days:
            dead.append(
                {
                    "product_id": nama_barang,
                    "product": nama_barang,
                    "last_sale": last_sale.date(),
                    "days_without_sales": days_without,
                    "status": "Potential Dead Stock",
                }
            )
    return dead


def get_product_sales_totals(db: Session) -> list[dict[str, object]]:
    """Return aggregated sales totals per product."""
    rows = (
        db.query(
            models.Sales.nama_barang,
            func.sum(models.Sales.kuantitas).label("total_qty"),
            func.sum(models.Sales.penjualan_bersih).label("total_revenue"),
        )
        .group_by(models.Sales.nama_barang)
        .order_by(func.sum(models.Sales.kuantitas).desc())
        .all()
    )

    return [
        {
            "product_id": r.nama_barang,
            "product": r.nama_barang,
            "total_qty": int(r.total_qty or 0),
            "total_revenue": float(r.total_revenue or 0.0),
        }
        for r in rows
    ]


def get_branch_performance(db: Session) -> list[dict[str, object]]:
    """Return branch performance if branch data is available.

    This is a best-effort implementation; if the Sales model doesn't contain a
    branch field, this returns an empty list.
    """
    if not hasattr(models.Sales, "branch"):
        return []

    rows = (
        db.query(
            models.Sales.branch.label("branch"),
            func.count(models.Sales.id).label("total_sales"),
            func.sum(models.Sales.kuantitas).label("total_revenue"),
        )
        .group_by(models.Sales.branch)
        .order_by(func.sum(models.Sales.kuantitas).desc())
        .all()
    )

    return [
        {
            "branch": r.branch,
            "total_sales": int(r.total_sales or 0),
            "total_revenue": float(r.total_revenue or 0.0),
        }
        for r in rows
    ]


def get_all_sales_as_dataframe(db: Session) -> pd.DataFrame:
    """Get all sales as a pandas DataFrame for ML processing."""
    rows = db.query(models.Sales).all()
    
    if not rows:
        return pd.DataFrame()
    
    data = []
    for row in rows:
        data.append({
            'tanggal': row.tanggal,
            'nama_barang': row.nama_barang,
            'kategori': row.kategori,
            'kuantitas': row.kuantitas,
            'day_type': row.day_type,
            'waktu': row.waktu,
        })
    
    df = pd.DataFrame(data)
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    return df


def get_monthly_data_for_forecasting(db: Session) -> pd.DataFrame:
    """Get monthly aggregated data for time series forecasting."""
    rows = db.query(models.Sales).order_by(models.Sales.tanggal).all()
    
    if not rows:
        return pd.DataFrame()
    
    monthly = {}
    for row in rows:
        month_key = row.tanggal.strftime("%Y-%m")
        monthly.setdefault(month_key, 0.0)
        monthly[month_key] += float(row.kuantitas or 0.0)
    
    df = pd.DataFrame([
        {'month': k, 'kuantitas': v}
        for k, v in sorted(monthly.items())
    ])
    
    df['month'] = pd.to_datetime(df['month'])
    return df.sort_values('month')


def get_product_sales_by_period(
    db: Session,
    product_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list[dict]:
    """Get sales data for a specific product within a period."""
    query = db.query(models.Sales).filter(models.Sales.nama_barang == product_name)
    
    if start_date:
        query = query.filter(models.Sales.tanggal >= start_date)
    if end_date:
        query = query.filter(models.Sales.tanggal <= end_date)
    
    rows = query.order_by(models.Sales.tanggal).all()
    
    return [
        {
            'tanggal': row.tanggal,
            'kuantitas': row.kuantitas,
            'kategori': row.kategori,
        }
        for row in rows
    ]


def get_sales_count(db: Session) -> int:
    """Get total number of sales records."""
    return db.query(models.Sales).count()


def get_date_range(db: Session) -> dict:
    """Get date range of sales data."""
    min_date = db.query(func.min(models.Sales.tanggal)).scalar()
    max_date = db.query(func.max(models.Sales.tanggal)).scalar()
    
    return {
        'min_date': min_date.isoformat() if min_date else None,
        'max_date': max_date.isoformat() if max_date else None,
    }
