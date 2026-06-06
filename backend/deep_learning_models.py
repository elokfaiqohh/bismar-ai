"""Deep Learning models for time series forecasting (LSTM/GRU)."""

from typing import Tuple, Optional
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model as keras_load_model
    from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    keras = None
    Sequential = None
    keras_load_model = None

from logger import get_logger
from exceptions import ModelTrainingError, InsufficientDataError, PredictionError
from config import settings

logger = get_logger("deep_learning")


class LSTMForecastModel:
    """LSTM model for monthly sales forecasting."""

    def __init__(self, units: int = 64, lookback_window: int = 12):
        """
        Initialize LSTM model.

        Parameters:
        -----------
        units : int
            Number of LSTM units
        lookback_window : int
            Number of previous months to look at for prediction
        """
        self.units = units
        self.lookback_window = lookback_window
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = None

    def prepare_data(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM training.

        Parameters:
        -----------
        data : np.ndarray
            1D array of monthly sales values

        Returns:
        --------
        X, y : Tuple of training features and targets
        """
        if len(data) < self.lookback_window + 1:
            raise InsufficientDataError(
                f"Need at least {self.lookback_window + 1} data points, got {len(data)}"
            )

        # Normalize data
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))

        X, y = [], []
        for i in range(len(scaled_data) - self.lookback_window):
            X.append(scaled_data[i : i + self.lookback_window])
            y.append(scaled_data[i + self.lookback_window])

        return np.array(X), np.array(y)

    def build_model(self) -> Sequential:
        """Build LSTM model architecture."""
        model = Sequential([
            LSTM(self.units, activation='relu', input_shape=(self.lookback_window, 1)),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model

    def train(
        self,
        data: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
    ) -> dict:
        """
        Train LSTM model.

        Parameters:
        -----------
        data : np.ndarray
            1D array of monthly sales values
        epochs : int
            Number of training epochs
        batch_size : int
            Batch size for training
        validation_split : float
            Validation split ratio

        Returns:
        --------
        dict : Training history and metrics
        """
        try:
            X, y = self.prepare_data(data)
            self.model = self.build_model()

            logger.info(f"Training LSTM model with {len(X)} samples")
            self.history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=0,
            )

            # Evaluate on training data
            train_pred = self.model.predict(X)
            train_r2 = r2_score(y, train_pred)
            train_mae = mean_absolute_error(y, train_pred)

            logger.info(f"LSTM Training - R²: {train_r2:.4f}, MAE: {train_mae:.4f}")

            return {
                "model_type": "LSTM",
                "train_r2": float(train_r2),
                "train_mae": float(train_mae),
                "epochs": epochs,
                "samples": len(X),
            }

        except Exception as e:
            logger.error(f"LSTM training failed: {str(e)}")
            raise ModelTrainingError(f"LSTM training failed: {str(e)}")

    def predict_next_month(self, data: np.ndarray) -> float:
        """
        Predict next month sales.

        Parameters:
        -----------
        data : np.ndarray
            1D array of recent monthly sales values

        Returns:
        --------
        float : Predicted sales for next month
        """
        if self.model is None:
            raise PredictionError("Model not trained yet")

        if len(data) < self.lookback_window:
            raise InsufficientDataError(
                f"Need at least {self.lookback_window} data points"
            )

        try:
            # Use last lookback_window values
            recent_data = data[-self.lookback_window:]
            scaled_data = self.scaler.transform(recent_data.reshape(-1, 1))
            X = scaled_data.reshape(1, self.lookback_window, 1)

            scaled_pred = self.model.predict(X, verbose=0)
            prediction = self.scaler.inverse_transform(scaled_pred)[0, 0]

            return max(float(prediction), 0.0)  # Ensure non-negative

        except Exception as e:
            logger.error(f"LSTM prediction failed: {str(e)}")
            raise PredictionError(f"LSTM prediction failed: {str(e)}")

    def save(self, path: str):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("No model to save")
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)
        
        # Save scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"LSTM model saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'LSTMForecastModel':
        """Load model from disk."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        instance = cls()
        instance.model = keras_load_model(path)
        
        # Load scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        if Path(scaler_path).exists():
            instance.scaler = joblib.load(scaler_path)
        
        logger.info(f"LSTM model loaded from {path}")
        return instance


class GRUForecastModel:
    """GRU model for monthly sales forecasting (similar to LSTM but faster)."""

    def __init__(self, units: int = 64, lookback_window: int = 12):
        """Initialize GRU model."""
        self.units = units
        self.lookback_window = lookback_window
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = None

    def prepare_data(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for GRU training."""
        if len(data) < self.lookback_window + 1:
            raise InsufficientDataError(
                f"Need at least {self.lookback_window + 1} data points, got {len(data)}"
            )

        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        X, y = [], []

        for i in range(len(scaled_data) - self.lookback_window):
            X.append(scaled_data[i : i + self.lookback_window])
            y.append(scaled_data[i + self.lookback_window])

        return np.array(X), np.array(y)

    def build_model(self) -> Sequential:
        """Build GRU model architecture."""
        model = Sequential([
            GRU(self.units, activation='relu', input_shape=(self.lookback_window, 1)),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model

    def train(
        self,
        data: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
    ) -> dict:
        """Train GRU model."""
        try:
            X, y = self.prepare_data(data)
            self.model = self.build_model()

            logger.info(f"Training GRU model with {len(X)} samples")
            self.history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=0,
            )

            # Evaluate
            train_pred = self.model.predict(X)
            train_r2 = r2_score(y, train_pred)
            train_mae = mean_absolute_error(y, train_pred)

            logger.info(f"GRU Training - R²: {train_r2:.4f}, MAE: {train_mae:.4f}")

            return {
                "model_type": "GRU",
                "train_r2": float(train_r2),
                "train_mae": float(train_mae),
                "epochs": epochs,
                "samples": len(X),
            }

        except Exception as e:
            logger.error(f"GRU training failed: {str(e)}")
            raise ModelTrainingError(f"GRU training failed: {str(e)}")

    def predict_next_month(self, data: np.ndarray) -> float:
        """Predict next month sales."""
        if self.model is None:
            raise PredictionError("Model not trained yet")

        if len(data) < self.lookback_window:
            raise InsufficientDataError(
                f"Need at least {self.lookback_window} data points"
            )

        try:
            recent_data = data[-self.lookback_window:]
            scaled_data = self.scaler.transform(recent_data.reshape(-1, 1))
            X = scaled_data.reshape(1, self.lookback_window, 1)

            scaled_pred = self.model.predict(X, verbose=0)
            prediction = self.scaler.inverse_transform(scaled_pred)[0, 0]

            return max(float(prediction), 0.0)

        except Exception as e:
            logger.error(f"GRU prediction failed: {str(e)}")
            raise PredictionError(f"GRU prediction failed: {str(e)}")

    def save(self, path: str):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("No model to save")
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)
        
        scaler_path = path.replace('.h5', '_scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"GRU model saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'GRUForecastModel':
        """Load model from disk."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        instance = cls()
        instance.model = keras_load_model(path)
        
        scaler_path = path.replace('.h5', '_scaler.pkl')
        if Path(scaler_path).exists():
            instance.scaler = joblib.load(scaler_path)
        
        logger.info(f"GRU model loaded from {path}")
        return instance
