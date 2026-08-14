from django.contrib import admin
from .models import MarketplaceListing, MarketplaceOrder, Wishlist, MarketplaceReview

# Class: MarketplaceOrderInline
class MarketplaceOrderInline(admin.TabularInline):
    model = MarketplaceOrder
    extra = 0
    readonly_fields = ('total_price', 'status', 'linked_order', 'created_at')

# Class: MarketplaceReviewInline
class MarketplaceReviewInline(admin.TabularInline):
    model = MarketplaceReview
    extra = 0

@admin.register(MarketplaceListing)
# Class: MarketplaceListingAdmin
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ('listing_title', 'product', 'business', 'listing_type', 'listing_status', 'discounted_price', 'quantity_available', 'views', 'purchase_count')
    list_filter = ('listing_status', 'listing_type', 'pricing_strategy', 'is_featured', 'visible_to_ngos')
    search_fields = ('listing_title', 'product__name')
    readonly_fields = ('id', 'views', 'wishlist_count', 'purchase_count', 'created_at', 'updated_at')
    inlines = [MarketplaceOrderInline, MarketplaceReviewInline]

@admin.register(Wishlist)
# Class: WishlistAdmin
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    search_fields = ('user__email', 'listing__listing_title')

@admin.register(MarketplaceOrder)
# Class: MarketplaceOrderAdmin
class MarketplaceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'customer', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('listing__listing_title', 'customer__first_name')
