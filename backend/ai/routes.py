from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

try:
    from .. import crud, schemas, database
    from ..services import prediction as prediction_service
except ImportError:  # pragma: no cover
    import crud, schemas, database
    from services import prediction as prediction_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/restock-recommendation", response_model=schemas.RestockRecommendationResponse)
def restock_recommendation(
    request: schemas.RestockRecommendationRequest, db: Session = Depends(database.get_db)
):
    """Recommend how many units should be restocked based on predicted demand."""
    product = crud.get_product_by_code(db=db, kode_produk=request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prediction = prediction_service.predict_product_sales(
        date_str=request.date.isoformat(),
        product_name=request.product_id,
    )

    predicted_demand = prediction["predicted_qty"]
    restock_needed = predicted_demand - request.current_stock
    recommended = max(restock_needed, 0)

    return {
        "product": product["nama_barang"],
        "predicted_demand": predicted_demand,
        "current_stock": request.current_stock,
        "recommended_restock": recommended,
    }


@router.get("/top-products", response_model=list[schemas.TopProductPrediction])
def top_products_tomorrow(db: Session = Depends(database.get_db)):
    """Return top 5 products by predicted sales quantity for tomorrow."""
    products = crud.get_products(db=db)
    if not products:
        return []

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    predictions = []
    for prod in products:
        try:
            result = prediction_service.predict_product_sales(
                date_str=tomorrow,
                product_name=prod["nama_barang"],
            )
            predictions.append(
                {"product": prod["nama_barang"], "predicted_qty": result["predicted_qty"]}
            )
        except Exception:
            # Skip products that cannot be predicted (missing model mapping etc.)
            continue

    # Sort descending by predicted quantity and return top 5
    sorted_preds = sorted(predictions, key=lambda p: p["predicted_qty"], reverse=True)
    return sorted_preds[:5]


@router.get("/dead-stock", response_model=list[schemas.DeadStockEntry])
def dead_stock(db: Session = Depends(database.get_db)):
    """Return products that have not had sales in the last 60 days."""
    dead = crud.get_dead_stock_products(db=db, cutoff_days=60)
    return dead


@router.post("/discount-simulation", response_model=list[schemas.DiscountSimulationEntry])
def discount_simulation(request: schemas.ProductPredictionRequest, db: Session = Depends(database.get_db)):
    """Simulate how different discount levels affect predicted demand."""
    product = crud.get_product_by_code(db=db, kode_produk=request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    discounts = [0.0, 5.0, 10.0, 15.0]
    results = []
    for d in discounts:
        try:
            prediction = prediction_service.predict_product_sales(
                date_str=request.date.isoformat(),
                product_name=request.product_id,
            )
            # Mock simulation logic since model doesn't support discount anymore
            mock_qty = int(prediction["predicted_qty"] * (1 + (d / 100.0)))
            results.append({"discount": d, "predicted_qty": mock_qty})
        except Exception:
            results.append({"discount": d, "predicted_qty": 0})

    return results


@router.get("/insights", response_model=list[schemas.Insight])
def insights(db: Session = Depends(database.get_db)):
    """Generate simple rule-based insights from sales data."""
    # Use pandas for quick time-window analysis
    import pandas as pd

    sales = crud.get_sales(db=db)
    if not sales:
        return [
            {"message": "No sales data available to generate insights."},
        ]

    df = pd.DataFrame(
        [
            {
                "tanggal": s.tanggal,
                "nama_barang": s.nama_barang,
                "kuantitas": s.kuantitas,
            }
            for s in sales
        ]
    )

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    today = pd.Timestamp(date.today())
    last_30 = today - pd.Timedelta(days=30)
    prev_30 = last_30 - pd.Timedelta(days=30)

    df_last_30 = df[df["tanggal"] >= last_30]
    df_prev_30 = df[(df["tanggal"] >= prev_30) & (df["tanggal"] < last_30)]

    insights = []

    # Insight 1: overall sales trend
    total_last_30 = df_last_30["kuantitas"].sum()
    total_prev_30 = df_prev_30["kuantitas"].sum()
    if total_prev_30 > 0:
        change_pct = (total_last_30 - total_prev_30) / total_prev_30 * 100.0
        if abs(change_pct) >= 10:
            direction = "increased" if change_pct > 0 else "decreased"
            insights.append(
                {
                    "message": f"Overall sales {direction} {abs(change_pct):.0f}% compared to the previous 30 days."
                }
            )

    # Insight 2: top product trend
    if not df_last_30.empty:
        top_last = (
            df_last_30.groupby("nama_barang")["kuantitas"].sum().sort_values(ascending=False).head(1)
        )
        if not top_last.empty:
            top_prod = top_last.index[0]
            insights.append({"message": f"Top product in the last 30 days is {top_prod}."})

    # Insight 3: dead stock reminder
    dead = crud.get_dead_stock_products(db=db, cutoff_days=60)
    if dead:
        insights.append(
            {
                "message": f"{len(dead)} products have not sold in the last 60 days and may be dead stock."  # noqa: E501
            }
        )

    if not insights:
        insights.append({"message": "Sales are stable. No strong trends detected."})

    return insights
