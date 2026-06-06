"""Machine Learning service layer - unified interface for all ML models."""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from sklearn.ensemble import VotingRegressor, RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import sys
import os

# Add backend directory to path for module resolution
sys.path.insert(0, os.path.dirname(__file__))

from logger import get_logger
from exceptions import ModelTrainingError, PredictionError, InsufficientDataError
from config import settings
from deep_learning_models import LSTMForecastModel, GRUForecastModel

# ProductClusteringManager will be imported lazily where needed to avoid circular imports
ProductClusteringManager = None

logger = get_logger("ml_service")
class EnsembleMLService:
    """Service for ensemble machine learning models (RF, GB, ET)."""

    def __init__(self):
        """Initialize ensemble service."""
        self.model = None
        self.trained = False

    def train_ensemble(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> Dict:
        """
        Train ensemble model.

        Parameters:
        -----------
        X : np.ndarray
            Training features
        y : np.ndarray
            Training target
        test_data : Optional[Tuple]
            (X_test, y_test) for evaluation

        Returns:
        --------
        Dict : Training metrics
        """
        try:
            logger.info(f"Training ensemble model with {len(X)} samples")

            # Create voting regressor with 3 models
            self.model = VotingRegressor(estimators=[
                ('rf', RandomForestRegressor(
                    n_estimators=settings.ENSEMBLE_N_ESTIMATORS,
                    random_state=settings.RANDOM_STATE,
                    n_jobs=-1
                )),
                ('gb', GradientBoostingRegressor(
                    n_estimators=settings.ENSEMBLE_N_ESTIMATORS,
                    random_state=settings.RANDOM_STATE
                )),
                ('et', ExtraTreesRegressor(
                    n_estimators=settings.ENSEMBLE_N_ESTIMATORS,
                    random_state=settings.RANDOM_STATE,
                    n_jobs=-1
                ))
            ])

            self.model.fit(X, y)
            self.trained = True

            # Evaluate on training data
            y_train_pred = self.model.predict(X)
            train_r2 = r2_score(y, y_train_pred)
            train_mae = mean_absolute_error(y, y_train_pred)

            metrics = {
                'model_type': 'Ensemble (RF+GB+ET)',
                'train_r2': float(train_r2),
                'train_mae': float(train_mae),
                'train_samples': len(X),
            }

            # Evaluate on test data if provided
            if test_data is not None:
                X_test, y_test = test_data
                y_test_pred = self.model.predict(X_test)
                test_r2 = r2_score(y_test, y_test_pred)
                test_mae = mean_absolute_error(y_test, y_test_pred)

                metrics['test_r2'] = float(test_r2)
                metrics['test_mae'] = float(test_mae)
                metrics['test_samples'] = len(X_test)

                logger.info(
                    f"Ensemble - Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}"
                )
            else:
                logger.info(f"Ensemble - Train R²: {train_r2:.4f}")

            return metrics

        except Exception as e:
            logger.error(f"Ensemble training failed: {str(e)}")
            raise ModelTrainingError(f"Ensemble training failed: {str(e)}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using ensemble model."""
        if not self.trained or self.model is None:
            raise PredictionError("Model not trained yet")

        try:
            predictions = self.model.predict(X)
            return np.maximum(predictions, 0)  # Ensure non-negative

        except Exception as e:
            logger.error(f"Ensemble prediction failed: {str(e)}")
            raise PredictionError(f"Ensemble prediction failed: {str(e)}")

    def save(self, path: str):
        """Save trained model."""
        if not self.trained or self.model is None:
            raise ValueError("No trained model to save")

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Ensemble model saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'EnsembleMLService':
        """Load trained model."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        instance = cls()
        instance.model = joblib.load(path)
        instance.trained = True
        logger.info(f"Ensemble model loaded from {path}")
        return instance


class MLPipelineManager:
    """Manages complete ML pipeline with multiple models."""

    def __init__(self):
        """Initialize ML pipeline manager."""
        self.ensemble_service = EnsembleMLService()
        self.lstm_model = None
        self.gru_model = None
        self.clustering_manager = None

    def train_all_models(
        self,
        monthly_data: np.ndarray,
        ensemble_X: np.ndarray,
        ensemble_y: np.ndarray,
        sales_df: pd.DataFrame,
    ) -> Dict:
        """
        Train all ML models.

        Parameters:
        -----------
        monthly_data : np.ndarray
            Monthly aggregated sales data for deep learning
        ensemble_X : np.ndarray
            Ensemble training features
        ensemble_y : np.ndarray
            Ensemble training target
        sales_df : pd.DataFrame
            Full sales dataframe for clustering

        Returns:
        --------
        Dict : Results from all model trainings
        """
        results = {}

        try:
            # Train ensemble
            logger.info("Training ensemble model...")
            results['ensemble'] = self.ensemble_service.train_ensemble(
                ensemble_X, ensemble_y
            )

            # Train LSTM if enough data
            if len(monthly_data) >= settings.LSTM_LOOKBACK_WINDOW + 1:
                logger.info("Training LSTM model...")
                self.lstm_model = LSTMForecastModel(
                    units=settings.LSTM_UNITS,
                    lookback_window=settings.LSTM_LOOKBACK_WINDOW
                )
                results['lstm'] = self.lstm_model.train(
                    monthly_data,
                    epochs=settings.LSTM_EPOCHS,
                    batch_size=settings.LSTM_BATCH_SIZE,
                    validation_split=settings.LSTM_VALIDATION_SPLIT,
                )
            else:
                logger.warning(
                    f"Not enough data for LSTM: need {settings.LSTM_LOOKBACK_WINDOW + 1}, "
                    f"got {len(monthly_data)}"
                )

            # Train GRU if enough data
            if len(monthly_data) >= settings.LSTM_LOOKBACK_WINDOW + 1:
                logger.info("Training GRU model...")
                self.gru_model = GRUForecastModel(
                    units=settings.LSTM_UNITS,
                    lookback_window=settings.LSTM_LOOKBACK_WINDOW
                )
                results['gru'] = self.gru_model.train(
                    monthly_data,
                    epochs=settings.LSTM_EPOCHS,
                    batch_size=settings.LSTM_BATCH_SIZE,
                    validation_split=settings.LSTM_VALIDATION_SPLIT,
                )
            else:
                logger.warning("Not enough data for GRU")

            # Train clustering
            if len(sales_df) > 0:
                logger.info("Training product clustering model...")
                # Lazy import to avoid circular dependency
                from clustering import ProductClusteringManager as PCM
                self.clustering_manager = PCM(
                    n_clusters=settings.KMEANS_N_CLUSTERS
                )
                results['clustering'] = self.clustering_manager.train(sales_df)
            else:
                logger.warning("No sales data for clustering")

            logger.info("All models trained successfully")
            return results

        except Exception as e:
            logger.error(f"ML pipeline training failed: {str(e)}")
            raise ModelTrainingError(f"ML pipeline training failed: {str(e)}")

    def predict_ensemble(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble predictions."""
        return self.ensemble_service.predict(X)

    def predict_lstm(self, data: np.ndarray) -> float:
        """Get LSTM next month prediction."""
        if self.lstm_model is None:
            raise PredictionError("LSTM model not trained")
        return self.lstm_model.predict_next_month(data)

    def predict_gru(self, data: np.ndarray) -> float:
        """Get GRU next month prediction."""
        if self.gru_model is None:
            raise PredictionError("GRU model not trained")
        return self.gru_model.predict_next_month(data)

    def ensemble_average_prediction(self, *predictions) -> float:
        """Average multiple predictions from different models."""
        valid_predictions = [p for p in predictions if p is not None and p > 0]
        if not valid_predictions:
            return 0.0
        return float(np.mean(valid_predictions))

    def get_best_prediction(self, *predictions) -> Tuple[float, str]:
        """Get the most conservative (lowest) prediction."""
        valid_predictions = [(p, name) for p, name in zip(predictions, 
                           ['Ensemble', 'LSTM', 'GRU']) if p is not None and p > 0]
        if not valid_predictions:
            return 0.0, "No predictions"

        best_pred, best_name = min(valid_predictions, key=lambda x: x[0])
        return float(best_pred), best_name

    def save_all_models(self):
        """Save all trained models."""
        try:
            if self.ensemble_service.trained:
                self.ensemble_service.save(settings.MODEL_PRODUCT_PATH)

            if self.lstm_model is not None:
                self.lstm_model.save(settings.MODEL_LSTM_PATH)

            if self.gru_model is not None:
                self.gru_model.save(settings.MODEL_GRU_PATH)

            if self.clustering_manager is not None:
                self.clustering_manager.save(settings.CLUSTERING_MODEL_PATH)

            logger.info("All models saved successfully")

        except Exception as e:
            logger.error(f"Failed to save models: {str(e)}")
            raise ModelTrainingError(f"Failed to save models: {str(e)}")

    @classmethod
    def load_all_models(cls) -> 'MLPipelineManager':
        """Load all trained models."""
        instance = cls()

        try:
            if Path(settings.MODEL_PRODUCT_PATH).exists():
                instance.ensemble_service = EnsembleMLService.load(
                    settings.MODEL_PRODUCT_PATH
                )

            if Path(settings.MODEL_LSTM_PATH).exists():
                instance.lstm_model = LSTMForecastModel.load(settings.MODEL_LSTM_PATH)

            if Path(settings.MODEL_GRU_PATH).exists():
                instance.gru_model = GRUForecastModel.load(settings.MODEL_GRU_PATH)

            if Path(settings.CLUSTERING_MODEL_PATH).exists():
                # Lazy import to avoid circular dependency
                from clustering import ProductClusteringManager as PCM
                instance.clustering_manager = PCM.load(
                    settings.CLUSTERING_MODEL_PATH
                )

            logger.info("All available models loaded successfully")

        except FileNotFoundError as e:
            logger.warning(f"Some models not found: {str(e)}")

        return instance
