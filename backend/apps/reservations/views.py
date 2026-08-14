from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from .models import Table, Reservation
from .serializers import TableSerializer, ReservationReadSerializer, ReservationWriteSerializer
from .services import ReservationService
from .filters import ReservationFilter
from .permissions import HasReservationManagementPermission

# Class: TableViewSet
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.filter(is_active=True)
    serializer_class = TableSerializer
    permission_classes = [HasReservationManagementPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['business', 'branch']

# Class: ReservationViewSet
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.filter(is_deleted=False)
    permission_classes = [HasReservationManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReservationFilter
    search_fields = [
        'reservation_number', 'customer__first_name', 
        'customer__last_name', 'customer__phone', 'items__product__name'
    ]
    ordering_fields = ['created_at', 'reservation_date', 'party_size']
    ordering = ['-created_at']

    # Method: get_serializer_class
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReservationWriteSerializer
        return ReservationReadSerializer

    @action(detail=True, methods=['post'])
    # Method: confirm
    def confirm(self, request, pk=None):
        try:
            reservation = ReservationService.confirm_reservation(str(pk), user=request.user)
            serializer = ReservationReadSerializer(reservation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: cancel
    def cancel(self, request, pk=None):
        try:
            remarks = request.data.get('remarks', 'User cancelled via API.')
            reservation = ReservationService.cancel_reservation(str(pk), user=request.user, remarks=remarks)
            serializer = ReservationReadSerializer(reservation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: convert_to_order
    def convert_to_order(self, request, pk=None):
        try:
            order = ReservationService.convert_to_order(str(pk), user=request.user)
            from apps.orders.serializers import OrderReadSerializer
            serializer = OrderReadSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
