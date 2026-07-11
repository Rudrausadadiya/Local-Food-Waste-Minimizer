from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NGOViewSet, DonationListingViewSet, DonationRequestViewSet, DonationPickupViewSet

router = DefaultRouter()
router.register(r'ngos', NGOViewSet, basename='ngo')
router.register(r'listings', DonationListingViewSet, basename='donationlisting')
router.register(r'requests', DonationRequestViewSet, basename='donationrequest')
router.register(r'pickups', DonationPickupViewSet, basename='donationpickup')

urlpatterns = [
    path('', include(router.urls)),
]
