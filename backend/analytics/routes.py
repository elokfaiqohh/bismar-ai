from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

try:
    from .. import crud, database
    from ..analytics_service import SalesAnalyticsService
    from ..logger import get_logger
except ImportError:  # pragma: no cover
    import crud, database
    from analytics_service import SalesAnalyticsService
    from logger import get_logger

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = get_logger("analytics_routes")


@router.get("/monthly-sales")
def monthly_sales(db: Session = Depends(database.get_db)):
    """Return monthly aggregated revenue (penjualan_bersih)."""
    return crud.get_monthly_sales(db=db)


@router.get("/product-sales")
def product_sales(db: Session = Depends(database.get_db)):
    """Return total sales (qty and revenue) per product."""
    return crud.get_product_sales_totals(db=db)


@router.get("/revenue-trend")
def revenue_trend(db: Session = Depends(database.get_db)):
    """Return monthly revenue trend (same as monthly sales)."""
    return crud.get_monthly_sales(db=db)


@router.get("/branch-performance")
def branch_performance(db: Session = Depends(database.get_db)):
    """Return branch performance sorted by revenue (if branch data exists)."""
    return crud.get_branch_performance(db=db)


@router.get("/sales-trend")
def sales_trend(
    db: Session = Depends(database.get_db),
    months_back: int = Query(12, ge=1, le=60),
    frequency: str = Query("month", regex="^(day|week|month)$")
):
    """
    Get sales trend over time with customizable frequency.
    
    Parameters:
    -----------
    months_back : int
        Number of months to look back (default: 12)
    frequency : str
        'day', 'week', or 'month' (default: 'month')
    """
    try:
        trend = SalesAnalyticsService.get_sales_trend(db, months_back, frequency)
        return {
            "frequency": frequency,
            "months_back": months_back,
            "data": trend
        }
    except Exception as e:
        logger.error(f"Error getting sales trend: {str(e)}")
        return {"error": "Failed to get sales trend"}


@router.get("/product-performance")
def product_performance(
    db: Session = Depends(database.get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get top performing products by total sales quantity.
    
    Parameters:
    -----------
    limit : int
        Number of top products to return (default: 20, max: 100)
    """
    try:
        products = SalesAnalyticsService.get_product_performance(db, limit)
        return {
            "count": len(products),
            "products": products
        }
    except Exception as e:
        logger.error(f"Error getting product performance: {str(e)}")
        return {"error": "Failed to get product performance"}


@router.get("/category-performance")
def category_performance(db: Session = Depends(database.get_db)):
    """Get sales performance by product category."""
    try:
        categories = SalesAnalyticsService.get_category_performance(db)
        return {
            "count": len(categories),
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error getting category performance: {str(e)}")
        return {"error": "Failed to get category performance"}


@router.get("/daily-statistics")
def daily_statistics(db: Session = Depends(database.get_db)):
    """Get statistics by day of week (sales patterns by day)."""
    try:
        daily_stats = SalesAnalyticsService.get_daily_statistics(db)
        return {
            "days": daily_stats
        }
    except Exception as e:
        logger.error(f"Error getting daily statistics: {str(e)}")
        return {"error": "Failed to get daily statistics"}


@router.get("/inventory-insights")
def inventory_insights(
    db: Session = Depends(database.get_db),
    dead_stock_days: int = Query(60, ge=30, le=365)
):
    """
    Get inventory insights including dead stock, slow movers, and active products.
    
    Parameters:
    -----------
    dead_stock_days : int
        Days without sales to consider as dead stock (default: 60)
    """
    try:
        insights = SalesAnalyticsService.get_inventory_insights(db, dead_stock_days)
        return insights
    except Exception as e:
        logger.error(f"Error getting inventory insights: {str(e)}")
        return {"error": "Failed to get inventory insights"}


@router.get("/time-of-day-analysis")
def time_of_day_analysis(db: Session = Depends(database.get_db)):
    """Get sales analysis by time of day (peak hours, patterns, etc)."""
    try:
        time_analysis = SalesAnalyticsService.get_time_of_day_analysis(db)
        return {
            "time_slots": time_analysis
        }
    except Exception as e:
        logger.error(f"Error getting time of day analysis: {str(e)}")
        return {"error": "Failed to get time of day analysis"}


@router.get("/dashboard-summary")
def dashboard_summary(db: Session = Depends(database.get_db)):
    """
    Get comprehensive dashboard summary with key metrics.
    
    This endpoint returns all key metrics for a quick overview.
    """
    try:
        total_sales = crud.get_sales_count(db)
        date_range = crud.get_date_range(db)
        monthly_data = crud.get_monthly_data_for_forecasting(db)
        
        avg_monthly = 0.0
        if len(monthly_data) > 0:
            avg_monthly = float(monthly_data['kuantitas'].mean())
        
        top_products = SalesAnalyticsService.get_product_performance(db, limit=5)
        inventory = SalesAnalyticsService.get_inventory_insights(db)
        
        return {
            "summary": {
                "total_sales_records": total_sales,
                "date_range": date_range,
                "avg_monthly_sales": avg_monthly,
                "total_months": len(monthly_data),
            },
            "top_products": top_products,
            "inventory": {
                "dead_stock_count": inventory.get('dead_stock_count', 0),
                "slow_movers_count": inventory.get('slow_movers_count', 0),
                "active_products_count": inventory.get('active_products_count', 0),
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        return {"error": "Failed to get dashboard summary"}
