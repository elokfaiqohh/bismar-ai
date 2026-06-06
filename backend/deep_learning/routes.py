"""Routes for Deep Learning forecasting models (LSTM/GRU)."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

try:
    from .. import database, crud
    from ..schemas import ProductPrediction
    from ..exceptions import PredictionError, InsufficientDataError
    from ..logger import get_logger
except ImportError:  # pragma: no cover
    import database
    import crud
    from schemas import ProductPrediction
    from exceptions import PredictionError, InsufficientDataError
    from logger import get_logger

router = APIRouter(prefix="/deep-learning", tags=["deep-learning"])
logger = get_logger("deep_learning_routes")

# Global ML pipeline (load on startup)
ml_pipeline = None


@router.on_event("startup")
def startup_load_models():
    """Load ML models on startup."""
    global ml_pipeline
    try:
        # Lazy import to avoid circular dependency
        from ..ml_service import MLPipelineManager
    except ImportError:
        from ml_service import MLPipelineManager
    try:
        ml_pipeline = MLPipelineManager.load_all_models()
        logger.info("Deep learning models loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load models on startup: {str(e)}")
        ml_pipeline = None


@router.get("/status")
def model_status():
    """Get status of deep learning models."""
    status = {
        'lstm_available': ml_pipeline and ml_pipeline.lstm_model is not None if ml_pipeline else False,
        'gru_available': ml_pipeline and ml_pipeline.gru_model is not None if ml_pipeline else False,
        'clustering_available': ml_pipeline and ml_pipeline.clustering_manager is not None if ml_pipeline else False,
    }
    return status


@router.get("/predict/lstm")
def predict_lstm_next_month(db: Session = Depends(database.get_db)):
    """
    Predict next month sales using LSTM model.

    Returns the predicted sales for the next month based on historical monthly trends.
    """
    if not ml_pipeline or ml_pipeline.lstm_model is None:
        raise HTTPException(
            status_code=503,
            detail="LSTM model not available. Train the model first."
        )

    try:
        monthly_df = crud.get_monthly_data_for_forecasting(db)

        if len(monthly_df) < 12:
            raise HTTPException(
                status_code=400,
                detail="Not enough historical data (need at least 12 months)"
            )

        monthly_data = monthly_df['kuantitas'].values

        prediction = ml_pipeline.predict_lstm(monthly_data)

        return {
            "model": "LSTM",
            "predicted_sales_next_month": float(prediction),
            "data_points": len(monthly_data),
            "method": "Long Short-Term Memory Neural Network"
        }

    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PredictionError as e:
        logger.error(f"LSTM prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")
    except Exception as e:
        logger.error(f"Unexpected error in LSTM prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/predict/gru")
def predict_gru_next_month(db: Session = Depends(database.get_db)):
    """
    Predict next month sales using GRU model.

    Returns the predicted sales for the next month based on historical monthly trends.
    GRU is faster than LSTM while maintaining similar performance.
    """
    if not ml_pipeline or ml_pipeline.gru_model is None:
        raise HTTPException(
            status_code=503,
            detail="GRU model not available. Train the model first."
        )

    try:
        monthly_df = crud.get_monthly_data_for_forecasting(db)

        if len(monthly_df) < 12:
            raise HTTPException(
                status_code=400,
                detail="Not enough historical data (need at least 12 months)"
            )

        monthly_data = monthly_df['kuantitas'].values
        prediction = ml_pipeline.predict_gru(monthly_data)

        return {
            "model": "GRU",
            "predicted_sales_next_month": float(prediction),
            "data_points": len(monthly_data),
            "method": "Gated Recurrent Unit Neural Network"
        }

    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PredictionError as e:
        logger.error(f"GRU prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")
    except Exception as e:
        logger.error(f"Unexpected error in GRU prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/predict/ensemble-comparison")
def compare_all_predictions(db: Session = Depends(database.get_db)):
    """
    Compare predictions from all available models (Ensemble, LSTM, GRU).

    This endpoint shows how different forecasting methods compare,
    helping you understand the range of predictions.
    """
    try:
        monthly_df = crud.get_monthly_data_for_forecasting(db)

        if len(monthly_df) < 12:
            raise HTTPException(
                status_code=400,
                detail="Not enough historical data (need at least 12 months)"
            )

        monthly_data = monthly_df['kuantitas'].values

        predictions = {
            'ensemble': None,
            'lstm': None,
            'gru': None,
            'average': None,
            'best_estimate': None,
        }

        # Try ensemble
        if ml_pipeline and ml_pipeline.ensemble_service.trained:
            try:
                import numpy as np
                X = np.array([[len(monthly_data) + 1]]).reshape(-1, 1)
                predictions['ensemble'] = float(ml_pipeline.predict_ensemble(X)[0])
            except Exception as e:
                logger.warning(f"Ensemble prediction failed: {str(e)}")

        # Try LSTM
        if ml_pipeline and ml_pipeline.lstm_model:
            try:
                predictions['lstm'] = ml_pipeline.predict_lstm(monthly_data)
            except Exception as e:
                logger.warning(f"LSTM prediction failed: {str(e)}")

        # Try GRU
        if ml_pipeline and ml_pipeline.gru_model:
            try:
                predictions['gru'] = ml_pipeline.predict_gru(monthly_data)
            except Exception as e:
                logger.warning(f"GRU prediction failed: {str(e)}")

        # Calculate average
        valid_preds = [p for p in [predictions['ensemble'], predictions['lstm'], predictions['gru']] if p is not None]
        if valid_preds:
            import numpy as np
            predictions['average'] = float(np.mean(valid_preds))
            predictions['best_estimate'] = float(np.min(valid_preds))  # Conservative estimate

        if not any([predictions['ensemble'], predictions['lstm'], predictions['gru']]):
            raise HTTPException(
                status_code=503,
                detail="No models available for prediction"
            )

        return {
            "predictions": predictions,
            "data_points": len(monthly_data),
            "description": "Comparison of different forecasting models"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.get("/model-info")
def get_model_info():
    """
    Get information about available deep learning models.

    Returns details about LSTM, GRU, and ensemble models.
    """
    info = {
        'lstm': {
            'available': ml_pipeline and ml_pipeline.lstm_model is not None if ml_pipeline else False,
            'type': 'Long Short-Term Memory',
            'description': 'Excellent for long-term dependencies in time series',
            'advantages': ['Handles long sequences', 'Remembers long-term patterns', 'Better for complex patterns'],
            'disadvantages': ['Slower training', 'More parameters', 'Needs more data'],
        },
        'gru': {
            'available': ml_pipeline and ml_pipeline.gru_model is not None if ml_pipeline else False,
            'type': 'Gated Recurrent Unit',
            'description': 'Faster alternative to LSTM with similar performance',
            'advantages': ['Faster training', 'Fewer parameters', 'Similar performance to LSTM'],
            'disadvantages': ['Less proven for very long sequences'],
        },
        'ensemble': {
            'available': ml_pipeline and ml_pipeline.ensemble_service.trained if ml_pipeline else False,
            'type': 'Voting Ensemble',
            'description': 'Combines Random Forest, Gradient Boosting, and Extra Trees',
            'advantages': ['Robust predictions', 'Handles non-linear relationships', 'Well-tested'],
            'disadvantages': ['No awareness of temporal patterns', 'Requires good features'],
        }
    }
    return info
