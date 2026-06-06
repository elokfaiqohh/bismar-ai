"""Custom exceptions for the application."""


class BismarException(Exception):
    """Base exception for Bismar application."""
    pass


class ValidationError(BismarException):
    """Raised when input validation fails."""
    pass


class DataNotFoundError(BismarException):
    """Raised when requested data is not found."""
    pass


class ModelTrainingError(BismarException):
    """Raised when model training fails."""
    pass


class PredictionError(BismarException):
    """Raised when prediction fails."""
    pass


class InsufficientDataError(BismarException):
    """Raised when there's not enough data for operation."""
    pass


class ClusteringError(BismarException):
    """Raised when clustering fails."""
    pass


class DatabaseError(BismarException):
    """Raised when database operations fail."""
    pass
