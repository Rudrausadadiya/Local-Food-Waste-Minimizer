from django.db import models
from django.utils import timezone
from common.models import UUIDTimeStampedModel
from apps.business.models import Business

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

class Category(UUIDTimeStampedModel):
    """
    Category model for grouping products.
    Supports nested categories via parent_category.
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    objects = models.Manager()
    available_objects = SoftDeleteManager()
    active_objects = ActiveManager()
    
    class Meta:
        unique_together = ('business', 'slug')
        verbose_name_plural = 'Categories'
        
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        
    def __str__(self):
        return self.name


class Product(UUIDTimeStampedModel):
    """
    Product model storing details like SKU, barcode, price, etc.
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    sku = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    allergens = models.TextField(blank=True, null=True)
    shelf_life_days = models.PositiveIntegerField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    objects = models.Manager()
    available_objects = SoftDeleteManager()
    active_objects = ActiveManager()
    
    class Meta:
        unique_together = ('business', 'sku')
        
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.product_name


class ProductImage(UUIDTimeStampedModel):
    """
    Model for storing additional product images.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.URLField()
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.product.product_name}"
