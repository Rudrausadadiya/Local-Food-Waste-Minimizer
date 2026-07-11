from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Inventory, StockTransaction, InventoryBatch, Supplier, WasteRecord
from .serializers import (
    InventorySerializer, StockTransactionSerializer, InventoryBatchSerializer,
    SupplierSerializer, WasteRecordSerializer, StockInSerializer,
    StockOutSerializer, StockTransferSerializer, RecordWasteSerializer
)
from .filters import InventoryFilter, InventoryBatchFilter, StockTransactionFilter
from .services import InventoryService
from .permissions import IsInventoryManager, IsBranchManager, IsReadOnlyStaff


@extend_schema_view(
    list=extend_schema(description="List all inventories"),
    retrieve=extend_schema(description="Get a specific inventory record"),
)
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('product', 'branch', 'business').all()
    serializer_class = InventorySerializer
    filterset_class = InventoryFilter
    permission_classes = [IsAuthenticated, IsReadOnlyStaff | IsInventoryManager | IsBranchManager]

    @extend_schema(request=StockInSerializer, responses={200: InventorySerializer})
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInventoryManager | IsBranchManager])
    def stock_in(self, request, pk=None):
        serializer = StockInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        batch_details = {
            'batch_number': data['batch_number'],
            'manufacturing_date': data.get('manufacturing_date'),
            'expiry_date': data.get('expiry_date'),
            'purchase_price': data.get('purchase_price', 0),
            'supplier_id': data.get('supplier'),
            'supplier_invoice_number': data.get('supplier_invoice_number'),
            'storage_location': data.get('storage_location'),
        }

        inventory = InventoryService.stock_in(
            inventory_id=pk,
            quantity=data['quantity'],
            user_id=request.user.id,
            batch_details=batch_details,
            reference_number=data.get('reference_number'),
            remarks=data.get('remarks')
        )
        
        return Response(self.get_serializer(inventory).data, status=status.HTTP_200_OK)

    @extend_schema(request=StockOutSerializer, responses={200: InventorySerializer})
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInventoryManager | IsBranchManager])
    def stock_out(self, request, pk=None):
        serializer = StockOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        inventory = InventoryService.stock_out(
            inventory_id=pk,
            quantity=data['quantity'],
            user_id=request.user.id,
            reference_number=data.get('reference_number'),
            remarks=data.get('remarks')
        )
        
        return Response(self.get_serializer(inventory).data, status=status.HTTP_200_OK)

    @extend_schema(request=StockTransferSerializer, responses={200: dict})
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInventoryManager])
    def transfer(self, request, pk=None):
        serializer = StockTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        InventoryService.stock_transfer(
            inventory_from_id=pk,
            inventory_to_id=data['inventory_to_id'],
            quantity=data['quantity'],
            user_id=request.user.id,
            reference_number=data.get('reference_number'),
            remarks=data.get('remarks')
        )
        
        return Response({"detail": "Transfer successful"}, status=status.HTTP_200_OK)

    @extend_schema(request=RecordWasteSerializer, responses={200: WasteRecordSerializer})
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInventoryManager | IsBranchManager])
    def waste(self, request, pk=None):
        serializer = RecordWasteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        waste_record = InventoryService.record_waste(
            inventory_id=pk,
            quantity=data['quantity'],
            reason=data['reason'],
            user_id=request.user.id,
            image=data.get('image'),
            remarks=data.get('remarks')
        )
        
        return Response(WasteRecordSerializer(waste_record).data, status=status.HTTP_200_OK)


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockTransaction.objects.all().order_by('-created_at')
    serializer_class = StockTransactionSerializer
    filterset_class = StockTransactionFilter
    permission_classes = [IsAuthenticated, IsReadOnlyStaff | IsInventoryManager | IsBranchManager]


class InventoryBatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryBatch.objects.all().order_by('expiry_date')
    serializer_class = InventoryBatchSerializer
    filterset_class = InventoryBatchFilter
    permission_classes = [IsAuthenticated, IsReadOnlyStaff | IsInventoryManager | IsBranchManager]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsInventoryManager]
