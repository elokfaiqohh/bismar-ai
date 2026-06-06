"""Shared prediction utilities for AI endpoints."""

# Support running both as a package and as a script.
try:
    from .. import ml_model
except ImportError:  # pragma: no cover
    import ml_model


def predict_product_sales(date_str: str, product_name: str) -> dict:
    """Proxy to the ML model prediction function.

    This layer exists so that AI endpoints can remain decoupled from the
    particular model implementation and makes it easier to swap models in the future.
    
    Parameters
    ----------
    date_str : str
        ISO date string (YYYY-MM-DD)
    product_name : str
        Product name (nama_barang)
    
    Returns
    -------
    dict
        {"predicted_qty": int}
    """
    return ml_model.predict_product_sales(
        date_str=date_str,
        product_name=product_name,
    )
