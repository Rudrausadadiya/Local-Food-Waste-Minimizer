from django.db import models
from django.utils import timezone
from common.models import UUIDTimeStampedModel
from apps.business.models import Business

# Class: SoftDeleteManager
class SoftDeleteManager(models.Manager):
    # Method: get_queryset
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# Class: ActiveManager
class ActiveManager(models.Manager):
    # Method: get_queryset
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

# Class: Category
class Category(UUIDTimeStampedModel):
    """
    Category model for grouping products.
    Supports nested categories via parent_category.
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    objects = models.Manager()
    available_objects = SoftDeleteManager()
    active_objects = ActiveManager()
    
    # Class: Meta
    class Meta:
        unique_together = ('business', 'slug')
        verbose_name_plural = 'Categories'
        
    # Method: soft_delete
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        
    # Method: __str__
    def __str__(self):
        return self.name


# Class: Product
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
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    objects = models.Manager()
    available_objects = SoftDeleteManager()
    active_objects = ActiveManager()
    
    # Class: Meta
    class Meta:
        unique_together = ('business', 'sku')
        
    # Method: soft_delete
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    # Method: __str__
    def __str__(self):
        return self.product_name


# Class: ProductImage
class ProductImage(UUIDTimeStampedModel):
    """
    Model for storing additional product images.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)
    
    # Method: __str__
    def __str__(self):
        return f"Image for {self.product.product_name}"
