import django_filters
from .models import Order

# Class: OrderFilter
class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='order_status', lookup_expr='iexact')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Class: Meta
    class Meta:
        model = Order
        fields = [
            'business',
            'branch',
            'customer',
            'order_status',
            'status',
            'payment_status',
            'payment_method'
        ]
