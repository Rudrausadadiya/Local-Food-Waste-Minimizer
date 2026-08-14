import django_filters
from .models import Reservation

# Class: ReservationFilter
class ReservationFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name='reservation_date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='reservation_date', lookup_expr='lte')
    
    # Class: Meta
    class Meta:
        model = Reservation
        fields = [
            'business',
            'branch',
            'customer',
            'reservation_status',
        ]
