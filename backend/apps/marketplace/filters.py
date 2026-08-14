import django_filters
from .models import MarketplaceListing

# Class: MarketplaceListingFilter
class MarketplaceListingFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="discounted_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="discounted_price", lookup_expr='lte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    
    # We allow filtering by category through the product relationship
    category = django_filters.CharFilter(field_name='product__category__name', lookup_expr='icontains')
    
    # Class: Meta
    class Meta:
        model = MarketplaceListing
        fields = [
            'business',
            'branch',
            'listing_type',
            'listing_status',
            'is_featured',
            'visible_to_ngos'
        ]
