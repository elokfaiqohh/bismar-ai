"""Product clustering for segmentation (Fast/Medium/Slow Moving)."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime, timedelta

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from logger import get_logger
from exceptions import ClusteringError, InsufficientDataError
from config import settings

logger = get_logger("clustering")

# Mapping cluster labels to meaningful names
CLUSTER_NAMES = {
    0: "Fast Moving",
    1: "Medium Moving",
    2: "Slow Moving",
}


class ProductClusteringManager:
    """Manages product clustering and segmentation."""

    def __init__(self, n_clusters: int = 3):
        """
        Initialize clustering manager.

        Parameters:
        -----------
        n_clusters : int
            Number of clusters for K-Means (default: 3 for Fast/Medium/Slow)
        """
        self.n_clusters = n_clusters
        self.model = None
        self.scaler = StandardScaler()
        self.products = None
        self.feature_names = None

    def extract_features(
        self,
        sales_df: pd.DataFrame,
        cutoff_date: datetime = None,
        lookback_days: int = 90,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Extract features for clustering from sales data.

        Parameters:
        -----------
        sales_df : pd.DataFrame
            Sales data with columns: tanggal, nama_barang, kuantitas
        cutoff_date : datetime, optional
            Date to cut off analysis (default: today)
        lookback_days : int
            Number of days to look back for feature extraction

        Returns:
        --------
        features_df : pd.DataFrame
            Features per product
        feature_names : List[str]
            Names of extracted features
        """
        if cutoff_date is None:
            cutoff_date = datetime.now()

        start_date = cutoff_date - timedelta(days=lookback_days)

        # Filter data
        filtered_df = sales_df[
            (sales_df['tanggal'] >= start_date) & (sales_df['tanggal'] <= cutoff_date)
        ].copy()

        if len(filtered_df) == 0:
            raise InsufficientDataError(
                f"No sales data found between {start_date} and {cutoff_date}"
            )

        features = []

        for product in filtered_df['nama_barang'].unique():
            product_data = filtered_df[filtered_df['nama_barang'] == product]

            # Feature 1: Total quantity sold
            total_qty = product_data['kuantitas'].sum()

            # Feature 2: Average daily sales
            unique_days = product_data['tanggal'].dt.date.nunique()
            avg_daily_qty = total_qty / max(unique_days, 1)

            # Feature 3: Number of sales transactions
            num_transactions = len(product_data)

            # Feature 4: Sales consistency (std dev of daily sales)
            daily_sales = product_data.groupby(product_data['tanggal'].dt.date)['kuantitas'].sum()
            sales_std = daily_sales.std() if len(daily_sales) > 1 else 0

            # Feature 5: Days since last sale
            last_sale = product_data['tanggal'].max()
            days_since_last = (cutoff_date - last_sale).days

            # Feature 6: First sale date (age of product in days)
            first_sale = product_data['tanggal'].min()
            product_age = (cutoff_date - first_sale).days

            features.append({
                'product': product,
                'total_qty': total_qty,
                'avg_daily_qty': avg_daily_qty,
                'num_transactions': num_transactions,
                'sales_std': sales_std,
                'days_since_last': days_since_last,
                'product_age': product_age,
            })

        features_df = pd.DataFrame(features)
        feature_cols = [
            'total_qty', 'avg_daily_qty', 'num_transactions',
            'sales_std', 'days_since_last', 'product_age'
        ]

        logger.info(f"Extracted features for {len(features_df)} products")
        return features_df, feature_cols

    def train(
        self,
        sales_df: pd.DataFrame,
        cutoff_date: datetime = None,
        lookback_days: int = 90,
    ) -> Dict:
        """
        Train clustering model.

        Parameters:
        -----------
        sales_df : pd.DataFrame
            Sales data
        cutoff_date : datetime, optional
            Date to cut off analysis
        lookback_days : int
            Number of days to look back

        Returns:
        --------
        dict : Training results with metrics
        """
        try:
            # Extract features
            features_df, feature_cols = self.extract_features(
                sales_df, cutoff_date, lookback_days
            )

            if len(features_df) < self.n_clusters:
                raise InsufficientDataError(
                    f"Need at least {self.n_clusters} products, found {len(features_df)}"
                )

            # Prepare data
            X = features_df[feature_cols].values
            X_scaled = self.scaler.fit_transform(X)

            # Train K-Means
            self.model = KMeans(
                n_clusters=self.n_clusters,
                random_state=settings.RANDOM_STATE,
                n_init=10,
            )
            labels = self.model.fit_predict(X_scaled)

            # Store products and feature names
            self.products = features_df.copy()
            self.products['cluster'] = labels
            self.feature_names = feature_cols

            # Calculate silhouette score
            silhouette = silhouette_score(X_scaled, labels)

            # Cluster sizes
            unique, counts = np.unique(labels, return_counts=True)
            cluster_sizes = {int(u): int(c) for u, c in zip(unique, counts)}

            logger.info(f"Clustering trained - Silhouette Score: {silhouette:.4f}")
            logger.info(f"Cluster distribution: {cluster_sizes}")

            return {
                "n_clusters": self.n_clusters,
                "n_products": len(features_df),
                "silhouette_score": float(silhouette),
                "cluster_sizes": cluster_sizes,
                "features_used": feature_cols,
            }

        except Exception as e:
            logger.error(f"Clustering training failed: {str(e)}")
            raise ClusteringError(f"Clustering training failed: {str(e)}")

    def predict_cluster(self, product_features: Dict) -> Tuple[int, str]:
        """
        Predict cluster for a product.

        Parameters:
        -----------
        product_features : Dict
            Product features (must match training features)

        Returns:
        --------
        cluster_id, cluster_name : Tuple
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        try:
            X = np.array([product_features[f] for f in self.feature_names]).reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            cluster_id = self.model.predict(X_scaled)[0]
            cluster_name = CLUSTER_NAMES.get(cluster_id, f"Cluster {cluster_id}")

            return int(cluster_id), cluster_name

        except Exception as e:
            logger.error(f"Cluster prediction failed: {str(e)}")
            raise ClusteringError(f"Cluster prediction failed: {str(e)}")

    def get_cluster_summary(self) -> List[Dict]:
        """Get summary statistics for each cluster."""
        if self.products is None:
            raise ValueError("Model not trained yet")

        summaries = []
        for cluster_id in range(self.n_clusters):
            cluster_data = self.products[self.products['cluster'] == cluster_id]

            summaries.append({
                'cluster_id': int(cluster_id),
                'cluster_name': CLUSTER_NAMES.get(cluster_id, f"Cluster {cluster_id}"),
                'num_products': len(cluster_data),
                'avg_total_qty': float(cluster_data['total_qty'].mean()),
                'avg_daily_qty': float(cluster_data['avg_daily_qty'].mean()),
                'avg_transactions': float(cluster_data['num_transactions'].mean()),
                'products': cluster_data['product'].tolist(),
            })

        return sorted(summaries, key=lambda x: x['avg_daily_qty'], reverse=True)

    def get_product_cluster(self, product_name: str) -> Dict:
        """Get cluster information for a specific product."""
        if self.products is None:
            raise ValueError("Model not trained yet")

        product_data = self.products[self.products['product'] == product_name]
        if len(product_data) == 0:
            raise ValueError(f"Product not found in clustering data: {product_name}")

        cluster_id = int(product_data['cluster'].iloc[0])
        cluster_name = CLUSTER_NAMES.get(cluster_id, f"Cluster {cluster_id}")

        return {
            'product': product_name,
            'cluster_id': cluster_id,
            'cluster_name': cluster_name,
            'total_qty': float(product_data['total_qty'].iloc[0]),
            'avg_daily_qty': float(product_data['avg_daily_qty'].iloc[0]),
            'num_transactions': int(product_data['num_transactions'].iloc[0]),
        }

    def save(self, path: str):
        """Save clustering model to disk."""
        if self.model is None:
            raise ValueError("No model to save")

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        data = {
            'model': self.model,
            'scaler': self.scaler,
            'products': self.products,
            'feature_names': self.feature_names,
            'n_clusters': self.n_clusters,
        }

        joblib.dump(data, path)
        logger.info(f"Clustering model saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'ProductClusteringManager':
        """Load clustering model from disk."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        data = joblib.load(path)

        instance = cls(n_clusters=data['n_clusters'])
        instance.model = data['model']
        instance.scaler = data['scaler']
        instance.products = data['products']
        instance.feature_names = data['feature_names']

        logger.info(f"Clustering model loaded from {path}")
        return instance
