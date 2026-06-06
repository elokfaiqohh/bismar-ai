"""Application configuration management."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_TITLE: str = "Indo Bismar AI Forecast"
    API_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = f"sqlite:///{Path(__file__).parent / 'sales.db'}"

    # ML Configuration
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    TRAIN_SIZE: float = 0.8
    
    # Ensemble Models
    ENSEMBLE_N_ESTIMATORS: int = 100
    
    # Deep Learning
    LSTM_UNITS: int = 64
    LSTM_EPOCHS: int = 50
    LSTM_BATCH_SIZE: int = 32
    LSTM_VALIDATION_SPLIT: float = 0.2
    LSTM_LOOKBACK_WINDOW: int = 12  # 12 months window
    
    # Clustering
    KMEANS_N_CLUSTERS: int = 3  # Fast, Medium, Slow Moving
    CLUSTERING_MIN_SAMPLES: int = 10
    
    # Model Paths
    MODEL_PRODUCT_PATH: str = str(Path(__file__).parent / "model_product_sales.pkl")
    MODEL_LSTM_PATH: str = str(Path(__file__).parent / "models" / "lstm_model.h5")
    MODEL_GRU_PATH: str = str(Path(__file__).parent / "models" / "gru_model.h5")
    CLUSTERING_MODEL_PATH: str = str(Path(__file__).parent / "models" / "kmeans_model.pkl")
    
    # Feature Configuration
    DEFAULT_MONTHLY_PREDICTIONS_AHEAD: int = 6  # Predict 6 months ahead
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # Change to specific domain in production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
