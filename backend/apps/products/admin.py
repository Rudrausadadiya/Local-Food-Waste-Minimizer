from django.contrib import admin
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'slug', 'is_active', 'is_deleted')
    search_fields = ('name', 'slug')
    list_filter = ('is_active', 'is_deleted', 'business')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'sku', 'business', 'category', 'selling_price', 'is_active', 'is_deleted')
    search_fields = ('product_name', 'sku', 'barcode')
    list_filter = ('is_active', 'is_deleted', 'business', 'category')
    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary')
