from datetime import date, datetime

from pydantic import BaseModel, Field


class SalesBase(BaseModel):
    tanggal: datetime = Field(..., description="Tanggal transaksi")
    nama_barang: str
    tipe_transaksi: str
    kuantitas: int
    satuan: str
    day_of_week: int
    nama_hari: str
    day_type: str
    tx_order: int
    total_per_day: int
    waktu_ratio: float
    waktu: str
    kategori: str
    harga_satuan: float = Field(default=0.0, description="Unit price")
    total_penjualan: float = Field(default=0.0, description="Total sales amount")
    diskon: float = Field(default=0.0, description="Discount percentage")
    penjualan_bersih: float = Field(default=0.0, description="Net revenue after discount")


class SalesCreate(SalesBase):
    pass


class SalesUpdate(BaseModel):
    tanggal: datetime | None = None
    nama_barang: str | None = None
    tipe_transaksi: str | None = None
    kuantitas: int | None = None
    satuan: str | None = None
    day_of_week: int | None = None
    nama_hari: str | None = None
    day_type: str | None = None
    tx_order: int | None = None
    total_per_day: int | None = None
    waktu_ratio: float | None = None
    waktu: str | None = None
    kategori: str | None = None
    harga_satuan: float | None = None
    total_penjualan: float | None = None
    diskon: float | None = None
    penjualan_bersih: float | None = None


from pydantic import ConfigDict


class Sales(SalesBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    nama_barang: str
    product_id: str
    nama_produk: str


class ProductPredictionRequest(BaseModel):
    date: datetime
    end_date: datetime | None = None
    product_id: str


class ProductPredictionDetail(BaseModel):
    product: str
    predicted_qty: int
    estimated_revenue: float = 0.0


class ProductPrediction(BaseModel):
    product: str
    predicted_qty: int
    estimated_revenue: float = 0.0
    details: list[ProductPredictionDetail] | None = None


class RestockRecommendationRequest(BaseModel):
    product_id: str
    current_stock: int
    date: date


class RestockRecommendationResponse(BaseModel):
    product: str
    predicted_demand: int
    current_stock: int
    recommended_restock: int


class TopProductPrediction(BaseModel):
    product: str
    predicted_qty: int


class DeadStockEntry(BaseModel):
    product: str
    last_sale: date | None = None
    days_without_sales: int
    status: str


class DiscountSimulationEntry(BaseModel):
    discount: float
    predicted_qty: int


class Insight(BaseModel):
    message: str


class BranchPerformance(BaseModel):
    branch: str
    total_sales: float
    total_revenue: float


class DatasetImportRequest(BaseModel):
    upload_id: str
    mode: str
