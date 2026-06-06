"""Advanced analytics services for business intelligence."""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from logger import get_logger
from exceptions import DataNotFoundError
import models

logger = get_logger("analytics")


class SalesAnalyticsService:
    """Advanced sales analytics and insights."""

    @staticmethod
    def get_sales_trend(
        db: Session,
        months_back: int = 12,
        frequency: str = 'month'
    ) -> List[Dict]:
        """
        Get sales trend over time.

        Parameters:
        -----------
        db : Session
            Database session
        months_back : int
            Number of months to look back
        frequency : str
            'day', 'week', or 'month'

        Returns:
        --------
        List[Dict] : Trend data with timestamps and metrics
        """
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)

        sales = db.query(
            models.Sales.tanggal,
            models.Sales.kuantitas
        ).filter(
            models.Sales.tanggal >= cutoff_date
        ).order_by(
            models.Sales.tanggal
        ).all()

        if not sales:
            return []

        df = pd.DataFrame(sales, columns=['tanggal', 'kuantitas'])
        df['tanggal'] = pd.to_datetime(df['tanggal'])

        if frequency == 'day':
            grouped = df.groupby(df['tanggal'].dt.date)
        elif frequency == 'week':
            grouped = df.groupby(df['tanggal'].dt.to_period('W'))
        else:  # month
            grouped = df.groupby(df['tanggal'].dt.to_period('M'))

        trend = grouped['kuantitas'].agg([
            ('total_qty', 'sum'),
            ('avg_qty', 'mean'),
            ('max_qty', 'max'),
            ('min_qty', 'min'),
            ('num_transactions', 'count'),
        ]).reset_index()

        trend['tanggal'] = trend['tanggal'].astype(str)

        return [row.to_dict() for _, row in trend.iterrows()]

    @staticmethod
    def get_product_performance(db: Session, limit: int = 20) -> List[Dict]:
        """
        Get top performing products by total sales.

        Parameters:
        -----------
        db : Session
            Database session
        limit : int
            Number of top products to return

        Returns:
        --------
        List[Dict] : Product performance metrics
        """
        results = db.query(
            models.Sales.nama_barang,
            models.Sales.kategori,
        ).all()

        if not results:
            return []

        # Group and aggregate
        product_data = {}
        for sale in db.query(models.Sales).all():
            if sale.nama_barang not in product_data:
                product_data[sale.nama_barang] = {
                    'nama_barang': sale.nama_barang,
                    'kategori': sale.kategori,
                    'total_qty': 0,
                    'num_transactions': 0,
                    'last_sale': None,
                    'first_sale': None,
                }

            product_data[sale.nama_barang]['total_qty'] += sale.kuantitas or 0
            product_data[sale.nama_barang]['num_transactions'] += 1

            if product_data[sale.nama_barang]['last_sale'] is None:
                product_data[sale.nama_barang]['last_sale'] = sale.tanggal
            else:
                product_data[sale.nama_barang]['last_sale'] = max(
                    product_data[sale.nama_barang]['last_sale'], sale.tanggal
                )

            if product_data[sale.nama_barang]['first_sale'] is None:
                product_data[sale.nama_barang]['first_sale'] = sale.tanggal
            else:
                product_data[sale.nama_barang]['first_sale'] = min(
                    product_data[sale.nama_barang]['first_sale'], sale.tanggal
                )

        # Sort and limit
        sorted_products = sorted(
            product_data.values(),
            key=lambda x: x['total_qty'],
            reverse=True
        )[:limit]

        for product in sorted_products:
            if product['last_sale']:
                days_since = (datetime.now() - product['last_sale']).days
                product['days_since_last_sale'] = days_since

            if product['first_sale'] and product['last_sale']:
                product_age = (product['last_sale'] - product['first_sale']).days
                product['product_age_days'] = max(product_age, 0)

            product['last_sale'] = product['last_sale'].isoformat() if product['last_sale'] else None
            product['first_sale'] = product['first_sale'].isoformat() if product['first_sale'] else None

        return sorted_products

    @staticmethod
    def get_category_performance(db: Session) -> List[Dict]:
        """Get sales performance by category."""
        sales = db.query(models.Sales).all()

        if not sales:
            return []

        category_data = {}
        for sale in sales:
            if sale.kategori not in category_data:
                category_data[sale.kategori] = {
                    'kategori': sale.kategori,
                    'total_qty': 0,
                    'num_products': set(),
                    'num_transactions': 0,
                }

            category_data[sale.kategori]['total_qty'] += sale.kuantitas or 0
            category_data[sale.kategori]['num_products'].add(sale.nama_barang)
            category_data[sale.kategori]['num_transactions'] += 1

        result = []
        for cat_data in category_data.values():
            cat_data['num_products'] = len(cat_data['num_products'])
            result.append(cat_data)

        return sorted(result, key=lambda x: x['total_qty'], reverse=True)

    @staticmethod
    def get_daily_statistics(db: Session) -> List[Dict]:
        """Get statistics by day of week."""
        sales = db.query(models.Sales).all()

        if not sales:
            return []

        day_data = {}
        for sale in sales:
            day = sale.nama_hari
            if day not in day_data:
                day_data[day] = {
                    'day': day,
                    'day_of_week': sale.day_of_week,
                    'total_qty': 0,
                    'num_transactions': 0,
                    'avg_qty_per_transaction': 0,
                }

            day_data[day]['total_qty'] += sale.kuantitas or 0
            day_data[day]['num_transactions'] += 1

        for day_info in day_data.values():
            if day_info['num_transactions'] > 0:
                day_info['avg_qty_per_transaction'] = (
                    day_info['total_qty'] / day_info['num_transactions']
                )

        return sorted(day_data.values(), key=lambda x: x['day_of_week'])

    @staticmethod
    def get_inventory_insights(
        db: Session,
        days_threshold: int = 60
    ) -> Dict:
        """
        Get inventory insights (dead stock, slow movers, etc).

        Parameters:
        -----------
        db : Session
            Database session
        days_threshold : int
            Days without sales to consider as dead stock

        Returns:
        --------
        Dict : Inventory insights
        """
        today = datetime.now()
        sales = db.query(models.Sales).all()

        if not sales:
            return {}

        # Build product statistics
        product_stats = {}
        for sale in sales:
            if sale.nama_barang not in product_stats:
                product_stats[sale.nama_barang] = {
                    'last_sale': sale.tanggal,
                    'total_qty': 0,
                    'num_transactions': 0,
                }

            product_stats[sale.nama_barang]['last_sale'] = max(
                product_stats[sale.nama_barang]['last_sale'],
                sale.tanggal
            )
            product_stats[sale.nama_barang]['total_qty'] += sale.kuantitas or 0
            product_stats[sale.nama_barang]['num_transactions'] += 1

        # Classify products
        dead_stock = []
        slow_movers = []
        active = []

        for product, stats in product_stats.items():
            days_since_last = (today - stats['last_sale']).days

            if days_since_last > days_threshold:
                dead_stock.append({
                    'product': product,
                    'days_without_sales': days_since_last,
                    'total_qty_sold': stats['total_qty'],
                })
            elif stats['num_transactions'] < 5:
                slow_movers.append({
                    'product': product,
                    'num_transactions': stats['num_transactions'],
                    'days_since_last_sale': days_since_last,
                    'total_qty': stats['total_qty'],
                })
            else:
                active.append({
                    'product': product,
                    'num_transactions': stats['num_transactions'],
                    'total_qty': stats['total_qty'],
                })

        return {
            'dead_stock_count': len(dead_stock),
            'slow_movers_count': len(slow_movers),
            'active_products_count': len(active),
            'dead_stock': dead_stock,
            'slow_movers': slow_movers,
            'active': active[:10],  # Top 10 active
        }

    @staticmethod
    def get_time_of_day_analysis(db: Session) -> List[Dict]:
        """Analyze sales by time of day."""
        sales = db.query(models.Sales).all()

        if not sales:
            return []

        time_data = {}
        for sale in sales:
            time_slot = sale.waktu if sale.waktu else "Unknown"
            if time_slot not in time_data:
                time_data[time_slot] = {
                    'time_slot': time_slot,
                    'total_qty': 0,
                    'num_transactions': 0,
                    'avg_qty': 0,
                }

            time_data[time_slot]['total_qty'] += sale.kuantitas or 0
            time_data[time_slot]['num_transactions'] += 1

        for time_info in time_data.values():
            if time_info['num_transactions'] > 0:
                time_info['avg_qty'] = time_info['total_qty'] / time_info['num_transactions']

        return list(time_data.values())
