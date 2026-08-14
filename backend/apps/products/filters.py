import django_filters
from .models import Product

# Class: ProductFilter
class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="selling_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="selling_price", lookup_expr='lte')
    barcode = django_filters.CharFilter(field_name="barcode", lookup_expr='iexact')
    sku = django_filters.CharFilter(field_name="sku", lookup_expr='iexact')
    product_name = django_filters.CharFilter(field_name="product_name", lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name="brand", lookup_expr='icontains')

    # Class: Meta
    class Meta:
        model = Product
        fields = ['business', 'category', 'is_active']
