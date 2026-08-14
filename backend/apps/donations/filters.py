import django_filters
from .models import DonationListing

# Class: DonationListingFilter
class DonationListingFilter(django_filters.FilterSet):
    available_until_before = django_filters.DateTimeFilter(field_name='available_until', lookup_expr='lte')
    available_until_after = django_filters.DateTimeFilter(field_name='available_until', lookup_expr='gte')
    
    # Class: Meta
    class Meta:
        model = DonationListing
        fields = [
            'business',
            'branch',
            'donation_status',
            'priority',
            'visible_to_verified_ngos'
        ]
