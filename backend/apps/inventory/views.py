from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Inventory, StockTransaction, InventoryBatch, Supplier
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
# Class: InventoryViewSet
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('product', 'branch', 'business').all()
    serializer_class = InventorySerializer
    filterset_class = InventoryFilter
    permission_classes = [IsAuthenticated, IsReadOnlyStaff | IsInventoryManager | IsBranchManager]

    @extend_schema(request=StockInSerializer, responses={200: InventorySerializer})
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsInventoryManager | IsBranchManager])
    # Method: stock_in
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
    # Method: stock_out
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
    # Method: transfer
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
    # Method: waste
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


# Class: StockTransactionViewSet
class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockTransaction.objects.all().order_by('-created_at')
    serializer_class = StockTransactionSerializer
    filterset_class = StockTransactionFilter
    permission_classes = [IsAuthenticated, IsReadOnlyStaff | IsInventoryManager | IsBranchManager]


# Class: InventoryBatchViewSet
class InventoryBatchViewSet(viewsets.ModelViewSet):
    queryset = InventoryBatch.objects.all().order_by('expiry_date')
    serializer_class = InventoryBatchSerializer
    filterset_class = InventoryBatchFilter
    permission_classes = [IsAuthenticated]

    # Method: create
    def create(self, request, *args, **kwargs):
        import uuid
        from decimal import Decimal
        from apps.products.models import Product, Category
        from apps.business.models import Business, Branch

        data = request.data
        product_name = data.get('product_name') or data.get('product')
        branch_id = data.get('branch_id') or data.get('branch')
        
        # If direct inventory ID is provided, check if valid
        inventory_id = data.get('inventory')
        if inventory_id and not product_name:
            return super().create(request, *args, **kwargs)

        user = request.user
        biz = user.businesses.filter(is_deleted=False).first() if user.is_authenticated else None
        if not biz:
            biz = Business.objects.filter(is_deleted=False).first()

        branch = None
        if branch_id:
            branch = Branch.objects.filter(id=branch_id).first()
        if not branch and biz:
            branch = biz.branches.first()

        product = None
        if product_name and biz:
            product = Product.objects.filter(business=biz, product_name__iexact=str(product_name).strip()).first()
            if not product:
                cat = Category.objects.filter(business=biz).first()
                if not cat:
                    cat = Category.objects.create(business=biz, name="General Food", slug=f"general-food-{uuid.uuid4().hex[:4]}")
                product = Product.objects.create(
                    business=biz,
                    category=cat,
                    product_name=str(product_name).strip(),
                    sku=f"SKU-{uuid.uuid4().hex[:6].upper()}",
                    unit="unit",
                    cost_price=Decimal(str(data.get('purchase_price', 0))),
                    selling_price=Decimal(str(data.get('purchase_price', 0))),
                    image=data.get('image'),
                    is_active=True
                )
            elif data.get('image') and not product.image:
                product.image = data.get('image')
                product.save()

        if not product or not branch:
            return super().create(request, *args, **kwargs)

        inventory, _ = Inventory.objects.get_or_create(
            business=biz,
            branch=branch,
            product=product,
            defaults={
                'current_stock': Decimal('0.00'),
                'unit_cost': Decimal(str(data.get('purchase_price', 0))),
                'average_cost': Decimal(str(data.get('purchase_price', 0))),
            }
        )

        expiry_date = data.get('expiry_date')
        if expiry_date:
            if isinstance(expiry_date, str):
                if 'T' in expiry_date:
                    expiry_date = expiry_date.split('T')[0]
                try:
                    from datetime import datetime
                    expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                except ValueError:
                    expiry_date = None

        batch_details = {
            'batch_number': data.get('batch_number') or f"BATCH-{uuid.uuid4().hex[:6].upper()}",
            'expiry_date': expiry_date,
            'purchase_price': Decimal(str(data.get('purchase_price', 0))),
            'storage_location': data.get('storage_location', 'ROOM_TEMP'),
        }

        qty = Decimal(str(data.get('quantity', 0)))
        InventoryService.stock_in(
            inventory_id=str(inventory.id),
            quantity=qty,
            user_id=request.user.id if request.user.is_authenticated else None,
            batch_details=batch_details,
            remarks=data.get('remarks', 'Stocked in new batch')
        )

        batch = InventoryBatch.objects.filter(inventory=inventory, batch_number=batch_details['batch_number']).first()
        if not batch:
            batch = InventoryBatch.objects.filter(inventory=inventory).order_by('-created_at').first()

        serializer = self.get_serializer(batch)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Class: SupplierViewSet
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsInventoryManager]
