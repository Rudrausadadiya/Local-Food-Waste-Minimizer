from rest_framework import serializers
from .models import Category, Product, ProductImage

# Class: CategorySerializer
class CategorySerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Category
        fields = ['id', 'business', 'name', 'slug', 'description', 'image', 'parent_category', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


# Class: ProductImageSerializer
class ProductImageSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


# Class: ProductSerializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Class: Meta
    class Meta:
        model = Product
        fields = [
            'id', 'business', 'category', 'sku', 'barcode', 'product_name', 
            'description', 'brand', 'unit', 'selling_price', 'cost_price', 
            'tax_rate', 'discount_percentage', 'allergens', 'shelf_life_days', 
            'image', 'is_active', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
