from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from .models import Customer, Order, Payment, Invoice, Sale
from .serializers import (
    CustomerSerializer, OrderReadSerializer, OrderWriteSerializer, 
    PaymentSerializer, InvoiceSerializer, SaleSerializer
)
from .services import OrderService, PaymentService, InvoiceService
from .filters import OrderFilter
from .permissions import HasOrderManagementPermission

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_deleted=False)
    serializer_class = CustomerSerializer
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['business', 'is_active']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__phone']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderWriteSerializer
        return OrderReadSerializer
        
    def perform_destroy(self, instance):
        try:
            OrderService.delete_order(str(instance.id))
        except ValidationError as e:
            raise ValidationError({'detail': str(e)})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        try:
            order = OrderService.complete_order(str(pk))
            serializer = OrderReadSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            order = OrderService.cancel_order(str(pk))
            serializer = OrderReadSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [HasOrderManagementPermission]

    def create(self, request, *args, **kwargs):
        try:
            payment = PaymentService.process_payment(
                order_id=request.data.get('order'),
                payment_data=request.data
            )
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        try:
            payment = PaymentService.process_refund(str(pk))
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['invoice_number']

    @action(detail=False, methods=['post'])
    def generate(self, request):
        try:
            order_id = request.data.get('order_id')
            invoice = InvoiceService.generate_invoice(order_id)
            serializer = self.get_serializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business', 'branch', 'sale_date']
    ordering_fields = ['sale_date', 'revenue']
