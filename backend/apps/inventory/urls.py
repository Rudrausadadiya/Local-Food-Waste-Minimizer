from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet, StockTransactionViewSet, InventoryBatchViewSet, SupplierViewSet

router = DefaultRouter()
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'transactions', StockTransactionViewSet, basename='stocktransaction')
router.register(r'batches', InventoryBatchViewSet, basename='inventorybatch')
router.register(r'suppliers', SupplierViewSet, basename='supplier')

urlpatterns = [
    path('', include(router.urls)),
]
