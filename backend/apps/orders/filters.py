import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Order
        fields = [
            'business',
            'branch',
            'customer',
            'order_status',
            'payment_status',
            'payment_method'
        ]
