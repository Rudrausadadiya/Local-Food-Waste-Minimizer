from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, MarketplaceOrderViewSet, WishlistViewSet, MarketplaceReviewViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'orders', MarketplaceOrderViewSet, basename='marketplaceorder')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'reviews', MarketplaceReviewViewSet, basename='marketplacereview')

urlpatterns = [
    path('', include(router.urls)),
]
