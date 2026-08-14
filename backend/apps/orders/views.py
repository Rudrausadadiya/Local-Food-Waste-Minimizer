from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.core.exceptions import ValidationError

from .models import Customer, Order, Payment, Invoice, Sale, LoyaltyTransaction
from .serializers import (
    CustomerSerializer, OrderReadSerializer, OrderWriteSerializer, 
    PaymentSerializer, InvoiceSerializer, SaleSerializer, LoyaltyTransactionSerializer, DeliverySerializer
)
from .services import OrderService, PaymentService, InvoiceService, DeliveryService
from .filters import OrderFilter
from .permissions import HasOrderManagementPermission

# Class: CustomerViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_deleted=False)
    serializer_class = CustomerSerializer
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['business', 'is_active']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    
    # Method: perform_destroy
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['get'])
    # Method: loyalty
    def loyalty(self, request, pk=None):
        from django.db.models import Sum
        customer = Customer.objects.filter(id=pk).first()
        if not customer:
            customer = Customer.objects.filter(user_id=pk).first()
        if not customer and request.user.is_authenticated:
            customer = Customer.objects.filter(email=request.user.email).first()

        if not customer:
            return Response({'loyalty_points': 0, 'history': []})

        total_points = Customer.objects.filter(
            models.Q(user=customer.user) | models.Q(email=customer.email)
        ).aggregate(total=Sum('loyalty_points'))['total'] or 0

        txs = LoyaltyTransaction.objects.filter(
            models.Q(customer__user=customer.user) | models.Q(customer__email=customer.email)
        ).order_by('-created_at')

        return Response({
            'loyalty_points': max(0, total_points),
            'history': LoyaltyTransactionSerializer(txs, many=True).data
        })

# Class: OrderViewSet
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(is_deleted=False)
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'customer__phone']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    # Method: get_queryset
    def get_queryset(self):
        qs = Order.objects.filter(is_deleted=False)
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return qs
        if getattr(user, 'role', '') == 'VENDOR':
            return qs.filter(business__owner=user)
        return qs.filter(customer__user=user)

    # Method: get_serializer_class
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderWriteSerializer
        return OrderReadSerializer
        
    # Method: perform_destroy
    def perform_destroy(self, instance):
        try:
            OrderService.delete_order(str(instance.id))
        except ValidationError as e:
            raise ValidationError({'detail': str(e)})

    @action(detail=True, methods=['post'])
    # Method: complete
    def complete(self, request, pk=None):
        try:
            order = OrderService.complete_order(str(pk))
            serializer = OrderReadSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: cancel
    def cancel(self, request, pk=None):
        try:
            order = OrderService.cancel_order(str(pk))
            serializer = OrderReadSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: dispatch_delivery
    def dispatch_delivery(self, request, pk=None):
        order = self.get_object()
        if not hasattr(order, 'delivery') or not order.delivery:
            return Response({'detail': 'Order does not have an associated delivery record.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delivery = DeliveryService.dispatch_delivery(str(order.delivery.id))
            return Response(DeliverySerializer(delivery).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: mark_delivered
    def mark_delivered(self, request, pk=None):
        order = self.get_object()
        if not hasattr(order, 'delivery') or not order.delivery:
            return Response({'detail': 'Order does not have an associated delivery record.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delivery = DeliveryService.mark_delivered(str(order.delivery.id))
            return Response(DeliverySerializer(delivery).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Class: PaymentViewSet
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [HasOrderManagementPermission]

    # Method: create
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
    # Method: refund
    def refund(self, request, pk=None):
        try:
            payment = PaymentService.process_refund(str(pk))
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Class: InvoiceViewSet
class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['invoice_number']

    @action(detail=False, methods=['post'])
    # Method: generate
    def generate(self, request):
        try:
            order_id = request.data.get('order_id')
            invoice = InvoiceService.generate_invoice(order_id)
            serializer = self.get_serializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Class: SaleViewSet
class SaleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [HasOrderManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business', 'branch', 'sale_date']
    ordering_fields = ['sale_date', 'revenue']
