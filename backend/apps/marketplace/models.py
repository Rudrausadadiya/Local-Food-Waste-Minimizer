import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Class: ListingType
class ListingType(models.TextChoices):
    STANDARD = 'STANDARD', _('Standard')
    CLEARANCE = 'CLEARANCE', _('Clearance')
    SURPLUS = 'SURPLUS', _('Surplus')
    DONATION = 'DONATION', _('Donation')

# Class: ListingStatus
class ListingStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    PUBLISHED = 'PUBLISHED', _('Published')
    PAUSED = 'PAUSED', _('Paused')
    UNPUBLISHED = 'UNPUBLISHED', _('Unpublished')
    CLOSED = 'CLOSED', _('Closed')
    EXPIRED = 'EXPIRED', _('Expired')

# Class: PricingStrategy
class PricingStrategy(models.TextChoices):
    MANUAL = 'MANUAL', _('Manual')
    AUTOMATIC = 'AUTOMATIC', _('Automatic')
    AI_RECOMMENDED = 'AI_RECOMMENDED', _('AI Recommended')

# Class: MarketplaceOrderStatus
class MarketplaceOrderStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')

# Class: MarketplaceListing
class MarketplaceListing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='marketplace_listings')
    branch = models.ForeignKey('business.Branch', on_delete=models.CASCADE, related_name='marketplace_listings')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='marketplace_listings')
    inventory_batch = models.ForeignKey('inventory.InventoryBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='marketplace_listings')
    
    listing_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    original_price = models.DecimalField(max_digits=12, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_available = models.PositiveIntegerField(default=0)
    
    listing_type = models.CharField(max_length=20, choices=ListingType.choices, default=ListingType.STANDARD)
    listing_status = models.CharField(max_length=20, choices=ListingStatus.choices, default=ListingStatus.DRAFT)
    pricing_strategy = models.CharField(max_length=20, choices=PricingStrategy.choices, default=PricingStrategy.MANUAL)
    
    expires_at = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='marketplace_images/', blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    visible_to_ngos = models.BooleanField(default=False, help_text="Make this listing visible to NGOs")
    
    # Metrics
    views = models.PositiveIntegerField(default=0)
    wishlist_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_listings')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin takedown metadata
    takedown_reason = models.CharField(max_length=500, blank=True, null=True, help_text="Reason given by Admin when taking down this listing")
    takedown_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when Admin took down this listing")

    # Class: Meta
    class Meta:
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"{self.listing_title} ({self.listing_status})"


# Class: MarketplaceOrder
class MarketplaceOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(MarketplaceListing, on_delete=models.PROTECT, related_name='orders')
    customer = models.ForeignKey('orders.Customer', on_delete=models.CASCADE, related_name='marketplace_orders')
    
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=MarketplaceOrderStatus.choices, default=MarketplaceOrderStatus.PENDING)
    
    # Link to the main order system for financial tracking
    linked_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='marketplace_orders')
    
    claim_expires_at = models.DateTimeField(blank=True, null=True, help_text="15-minute pickup hold expiry")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"Order for {self.quantity}x {self.listing.listing_title}"


# Class: Wishlist
class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    # Class: Meta
    class Meta:
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"{self.user} -> {self.listing.listing_title}"


# Class: MarketplaceReview
class MarketplaceReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey('orders.Customer', on_delete=models.CASCADE, related_name='marketplace_reviews')
    
    rating = models.PositiveIntegerField(help_text="Rating from 1 to 5")
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        unique_together = ('listing', 'customer')
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"Review {self.rating}/5 for {self.listing.listing_title}"
