import django_filters
from .models import Inventory, InventoryBatch, StockTransaction

class InventoryFilter(django_filters.FilterSet):
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    class Meta:
        model = Inventory
        fields = {
            'business': ['exact'],
            'branch': ['exact'],
            'product': ['exact'],
            'is_active': ['exact'],
        }

    def filter_low_stock(self, queryset, name, value):
        if value:
            # Requires F expression import, which is better handled via the model/repo
            # For simplicity in filter, we can do a query that compares the fields
            from django.db.models import F
            return queryset.filter(current_stock__lte=F('reorder_level'))
        return queryset


class InventoryBatchFilter(django_filters.FilterSet):
    class Meta:
        model = InventoryBatch
        fields = {
            'inventory': ['exact'],
            'batch_number': ['exact', 'icontains'],
            'status': ['exact'],
            'expiry_date': ['lte', 'gte'],
        }


class StockTransactionFilter(django_filters.FilterSet):
    class Meta:
        model = StockTransaction
        fields = {
            'inventory': ['exact'],
            'transaction_type': ['exact'],
            'created_at': ['lte', 'gte'],
            'source': ['exact'],
            'destination': ['exact'],
        }
