import csv
from io import StringIO
from typing import Dict, Any, List
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

from apps.inventory.models import Inventory
from apps.orders.models import Order
from apps.reservations.models import Reservation
from .dashboard import DashboardKPIBuilder
from .repositories import AnalyticsSnapshotRepository
from .exports import ExportAdapter

# Class: DashboardService
class DashboardService:
    @staticmethod
    # Method: get_dashboard_summary
    def get_dashboard_summary(start_date, end_date, business_id: str = None) -> Dict[str, Any]:
        """
        Calculates KPIs dynamically. Could leverage AnalyticsSnapshotRepository for caching
        in a full production environment via Celery.
        """
        snapshot = AnalyticsSnapshotRepository.get_latest('DASHBOARD_KPI', business_id)
        if snapshot and snapshot.data:
            return snapshot.data
        
        kpis = DashboardKPIBuilder.get_executive_kpis(start_date, end_date, business_id)
        
        AnalyticsSnapshotRepository.create({
            'snapshot_type': 'DASHBOARD_KPI',
            'business_id': business_id,
            'data': kpis
        })
        
        return kpis


# Class: DataQualityService
class DataQualityService:
    @staticmethod
    # Method: detect_anomalies
    def detect_anomalies(business_id: str = None) -> Dict[str, Any]:
        """
        Checks inconsistent data: negative inventory stocks, orphaned orders (orders with 0 items),
        and unlinked table reservations (reservations of type TABLE with 0 assigned tables).
        """
        inv_qs = Inventory.objects.filter(current_stock__lt=0)
        order_qs = Order.objects.annotate(item_count=Count('items')).filter(item_count=0)
        res_qs = Reservation.objects.annotate(table_count=Count('reserved_tables')).filter(
            reservation_type='TABLE', table_count=0
        )

        if business_id:
            inv_qs = inv_qs.filter(business_id=business_id)
            order_qs = order_qs.filter(business_id=business_id)
            res_qs = res_qs.filter(business_id=business_id)

        return {
            'negative_inventory': inv_qs.count(),
            'orphaned_orders': order_qs.count(),
            'unlinked_reservations': res_qs.count()
        }


# Class: DatasetService
class DatasetService:
    @staticmethod
    # Method: extract_training_dataset
    def extract_training_dataset(model_type: str, business_id: str = None) -> str:
        """
        Extracts structured historical sales data formatted as a CSV dataset for ML models.
        Note: Weather/temperature columns were omitted as external weather APIs are out of scope.
        """
        order_qs = Order.objects.all()
        if business_id:
            order_qs = order_qs.filter(business_id=business_id)

        daily_sales = (
            order_qs.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(sales_volume=Sum('total_amount'))
            .order_by('date')
        )

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['date', 'sales_volume'])

        for row in daily_sales:
            date_str = row['date'].strftime('%Y-%m-%d') if row['date'] else ''
            writer.writerow([date_str, float(row['sales_volume'] or 0)])

        return output.getvalue()


# Class: ReportService
class ReportService:
    @staticmethod
    # Method: generate_report
    def generate_report(report_type: str, start_date, end_date, export_format: str, business_id: str = None) -> str:
        """
        Fetches querysets for report generation and formats output via ExportAdapter.
        """
        data: List[Dict[str, Any]] = []

        if report_type == 'SALES':
            qs = Order.objects.filter(created_at__range=(start_date, end_date))
            if business_id:
                qs = qs.filter(business_id=business_id)
            data = [
                {
                    'order_number': o.order_number,
                    'total_amount': float(o.total_amount),
                    'status': o.order_status,
                    'created_at': str(o.created_at),
                }
                for o in qs
            ]
        elif report_type == 'INVENTORY':
            qs = Inventory.objects.select_related('product', 'branch').all()
            if business_id:
                qs = qs.filter(business_id=business_id)
            data = [
                {
                    'product_name': i.product.product_name if i.product else '',
                    'current_stock': float(i.current_stock),
                    'branch_name': i.branch.branch_name if i.branch else '',
                }
                for i in qs
            ]

        fmt = (export_format or 'CSV').upper()
        if fmt == 'JSON':
            return ExportAdapter.to_json(data)
        elif fmt == 'EXCEL':
            return ExportAdapter.to_excel(data)
        elif fmt == 'PDF':
            return ExportAdapter.to_pdf(data)
            
        return ExportAdapter.to_csv(data)
