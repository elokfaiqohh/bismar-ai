"""Routes for product clustering and segmentation."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

try:
    from .. import database, crud
    from ..exceptions import ClusteringError
    from ..logger import get_logger
except ImportError:  # pragma: no cover
    import database
    import crud
    from exceptions import ClusteringError
    from logger import get_logger

router = APIRouter(prefix="/clustering", tags=["clustering"])
logger = get_logger("clustering_routes")

# Global clustering manager (load on startup)
clustering_manager = None


@router.on_event("startup")
def startup_load_clustering():
    """Load clustering model on startup."""
    global clustering_manager
    try:
        # Lazy import to avoid circular dependency
        try:
            from ..ml_service import MLPipelineManager
        except ImportError:
            from ml_service import MLPipelineManager
        
        ml_pipeline = MLPipelineManager.load_all_models()
        clustering_manager = ml_pipeline.clustering_manager
        logger.info("Clustering model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load clustering model: {str(e)}")
        clustering_manager = None


@router.get("/status")
def clustering_status():
    """Get status of clustering model."""
    return {
        'clustering_available': clustering_manager is not None,
    }


@router.get("/summary")
def get_cluster_summary():
    """
    Get summary of all product clusters (Fast/Medium/Slow Moving).

    This shows how many products fall into each category based on sales performance.
    """
    if not clustering_manager:
        raise HTTPException(
            status_code=503,
            detail="Clustering model not available. Train the model first."
        )

    try:
        summary = clustering_manager.get_cluster_summary()

        return {
            "clusters": summary,
            "description": "Product segmentation based on sales velocity and consistency"
        }

    except ClusteringError as e:
        logger.error(f"Clustering summary error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cluster summary")
    except Exception as e:
        logger.error(f"Unexpected error in clustering summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/product/{product_name}")
def get_product_cluster(product_name: str):
    """
    Get cluster information for a specific product.

    Shows which cluster (Fast/Medium/Slow Moving) the product belongs to.
    """
    if not clustering_manager:
        raise HTTPException(
            status_code=503,
            detail="Clustering model not available"
        )

    try:
        cluster_info = clustering_manager.get_product_cluster(product_name)
        return cluster_info

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClusteringError as e:
        logger.error(f"Product cluster lookup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get product cluster")
    except Exception as e:
        logger.error(f"Unexpected error in product cluster lookup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/fast-moving")
def get_fast_moving_products():
    """Get all fast-moving products."""
    if not clustering_manager or clustering_manager.products is None:
        raise HTTPException(
            status_code=503,
            detail="Clustering model not available"
        )

    try:
        products = clustering_manager.products[
            clustering_manager.products['cluster'] == 0
        ][['product', 'total_qty', 'avg_daily_qty']].to_dict('records')

        return {
            'category': 'Fast Moving',
            'count': len(products),
            'products': products
        }

    except Exception as e:
        logger.error(f"Error fetching fast-moving products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.get("/medium-moving")
def get_medium_moving_products():
    """Get all medium-moving products."""
    if not clustering_manager or clustering_manager.products is None:
        raise HTTPException(
            status_code=503,
            detail="Clustering model not available"
        )

    try:
        products = clustering_manager.products[
            clustering_manager.products['cluster'] == 1
        ][['product', 'total_qty', 'avg_daily_qty']].to_dict('records')

        return {
            'category': 'Medium Moving',
            'count': len(products),
            'products': products
        }

    except Exception as e:
        logger.error(f"Error fetching medium-moving products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.get("/slow-moving")
def get_slow_moving_products():
    """Get all slow-moving products."""
    if not clustering_manager or clustering_manager.products is None:
        raise HTTPException(
            status_code=503,
            detail="Clustering model not available"
        )

    try:
        products = clustering_manager.products[
            clustering_manager.products['cluster'] == 2
        ][['product', 'total_qty', 'avg_daily_qty']].to_dict('records')

        return {
            'category': 'Slow Moving',
            'count': len(products),
            'products': products
        }

    except Exception as e:
        logger.error(f"Error fetching slow-moving products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.get("/info")
def clustering_info():
    """Get information about product clustering."""
    return {
        'description': 'Product clustering segments products into three categories',
        'categories': {
            'fast_moving': {
                'description': 'Products with high sales velocity and consistency',
                'characteristics': 'High total quantity, high daily average, many transactions',
                'recommendation': 'Maintain stock levels, focus on distribution efficiency'
            },
            'medium_moving': {
                'description': 'Products with moderate sales velocity',
                'characteristics': 'Moderate total quantity, moderate daily average',
                'recommendation': 'Balanced inventory management'
            },
            'slow_moving': {
                'description': 'Products with low sales velocity',
                'characteristics': 'Low total quantity, low daily average, few transactions',
                'recommendation': 'Consider promotions, bundling, or discontinuation'
            }
        },
        'method': 'K-Means clustering with features: total_qty, avg_daily_qty, num_transactions, sales_std, days_since_last, product_age',
        'lookback_period': '90 days'
    }
