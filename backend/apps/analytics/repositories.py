from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, Sum, Count, Avg, F
from django.utils import timezone
from .models import AnalyticsSnapshot, ScheduledReport, AnalyticsExportLog

class AnalyticsSnapshotRepository:
    @staticmethod
    def get_latest(snapshot_type: str, business_id: str = None) -> Optional[AnalyticsSnapshot]:
        qs = AnalyticsSnapshot.objects.filter(snapshot_type=snapshot_type)
        if business_id:
            qs = qs.filter(business_id=business_id)
        return qs.first()

    @staticmethod
    def create(data: Dict[str, Any]) -> AnalyticsSnapshot:
        return AnalyticsSnapshot.objects.create(**data)

class AnalyticsExportLogRepository:
    @staticmethod
    def create(data: Dict[str, Any]) -> AnalyticsExportLog:
        return AnalyticsExportLog.objects.create(**data)

    @staticmethod
    def update(log: AnalyticsExportLog, data: Dict[str, Any]) -> AnalyticsExportLog:
        for key, value in data.items():
            setattr(log, key, value)
        log.save()
        return log


class CrossModuleAnalyticsRepository:
    """
    Optimized repositories for cross-module queries.
    Uses select_related, prefetch_related, only, defer, and annotations heavily.
    """

    @staticmethod
    def get_sales_summary(start_date, end_date, business_id: str = None) -> Dict[str, Any]:
        from apps.orders.models import Order, OrderStatus
        
        qs = Order.objects.filter(
            created_at__range=(start_date, end_date),
            status=OrderStatus.DELIVERED
        )
        if business_id:
            qs = qs.filter(business_id=business_id)
            
        return qs.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
            average_order_value=Avg('total_amount')
        )

    @staticmethod
    def get_inventory_summary(business_id: str = None) -> Dict[str, Any]:
        from apps.inventory.models import Inventory
        
        qs = Inventory.objects.select_related('product', 'branch').only(
            'current_stock', 'product__price', 'reorder_level', 'branch_id'
        )
        if business_id:
            qs = qs.filter(branch__business_id=business_id)
            
        # Calculate Value
        total_value = sum(item.current_stock * item.product.price for item in qs if item.product.price)
        low_stock_count = qs.filter(current_stock__lte=F('reorder_level')).count()
        
        return {
            'total_value': total_value,
            'low_stock_count': low_stock_count
        }

    @staticmethod
    def get_donation_impact(start_date, end_date, business_id: str = None) -> Dict[str, Any]:
        from apps.donations.models import DonationImpact
        
        qs = DonationImpact.objects.select_related(
            'donation_pickup__donation_request__donation_listing__business'
        ).filter(calculated_at__range=(start_date, end_date))
        
        if business_id:
            qs = qs.filter(donation_pickup__donation_request__donation_listing__business_id=business_id)
            
        return qs.aggregate(
            meals_served=Sum('meals_served'),
            carbon_saved=Sum('carbon_saved_kg'),
            food_saved=Sum('food_saved_kg')
        )

    @staticmethod
    def get_marketplace_summary(start_date, end_date, business_id: str = None) -> Dict[str, Any]:
        from apps.marketplace.models import MarketplaceOrder, MarketplaceOrderStatus
        
        qs = MarketplaceOrder.objects.filter(
            created_at__range=(start_date, end_date),
            order_status=MarketplaceOrderStatus.COMPLETED
        )
        if business_id:
            qs = qs.filter(listing__business_id=business_id)
            
        return qs.aggregate(
            marketplace_revenue=Sum('total_amount'),
            marketplace_orders=Count('id')
        )
