from datetime import date

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(DateTime, nullable=False)
    nama_barang = Column(String, nullable=False)
    tipe_transaksi = Column(String, nullable=False)
    kuantitas = Column(Integer, nullable=False)
    satuan = Column(String, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    nama_hari = Column(String, nullable=False)
    day_type = Column(String, nullable=False)
    tx_order = Column(Integer, nullable=False)
    total_per_day = Column(Integer, nullable=False)
    waktu_ratio = Column(Float, nullable=False)
    waktu = Column(String, nullable=False)
    kategori = Column(String, nullable=False)
    # NEW: Pricing columns for revenue calculation
    harga_satuan = Column(Float, nullable=True, default=0.0)  # Unit price
    total_penjualan = Column(Float, nullable=True, default=0.0)  # Total sales (qty × harga_satuan)
    diskon = Column(Float, nullable=True, default=0.0)  # Discount percentage
    penjualan_bersih = Column(Float, nullable=True, default=0.0)  # Net revenue after discount
