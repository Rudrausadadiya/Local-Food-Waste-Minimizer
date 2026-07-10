from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, BranchViewSet, AddressViewSet, OperatingHoursViewSet

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'operating-hours', OperatingHoursViewSet, basename='operating-hours')

urlpatterns = [
    path('', include(router.urls)),
]
