from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NGOViewSet, DonationListingViewSet, DonationRequestViewSet,
    DonationPickupViewSet, NGOImpactSummaryView, DonationImpactViewSet,
    PickupRouteViewSet
)

router = DefaultRouter()
router.register(r'ngos', NGOViewSet, basename='ngo')
router.register(r'listings', DonationListingViewSet, basename='donationlisting')
router.register(r'requests', DonationRequestViewSet, basename='donationrequest')
router.register(r'pickups', DonationPickupViewSet, basename='donationpickup')
router.register(r'impacts', DonationImpactViewSet, basename='donationimpact')
router.register(r'routes', PickupRouteViewSet, basename='pickuproute')

urlpatterns = [
    path('impact/summary/', NGOImpactSummaryView.as_view(), name='ngo-impact-summary'),
    path('', include(router.urls)),
]
