from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Business, Branch, Address, OperatingHours
from .serializers import BusinessSerializer, BranchSerializer, AddressSerializer, OperatingHoursSerializer
from .repositories import BusinessRepository
from .services import (
    BusinessRegistrationService, BusinessUpdateService, BusinessVerificationService,
    BusinessDeactivationService, BranchManagementService, AddressManagementService,
    OperatingHoursService, BusinessAnalyticsService
)
from .permissions import IsBusinessOwner, CustomerCannotCreateBusiness

# Class: BusinessViewSet
class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsBusinessOwner, CustomerCannotCreateBusiness]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business_type', 'business_status', 'is_verified', 'is_active']
    search_fields = ['business_name', 'business_email', 'business_phone', 'description']
    ordering_fields = ['created_at', 'business_name', 'average_rating']
    ordering = ['-created_at']

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'ADMIN'):
            return Business.objects.filter(is_deleted=False)
        if user.is_authenticated and getattr(user, 'role', '') in ['VENDOR', 'NGO']:
            qs = Business.objects.filter(owner=user, is_deleted=False)
            if not qs.exists():
                biz_name = f"{user.first_name}'s Store" if user.first_name else "Merchant Store"
                b = BusinessRegistrationService.register_business(user, {
                    'business_name': biz_name,
                    'business_type': user.role if user.role in ['VENDOR', 'NGO'] else 'VENDOR',
                    'business_email': user.email,
                    'business_phone': getattr(user, 'phone_number', '') or '+91 98765 00000',
                    'business_status': 'PENDING',
                    'is_active': True,
                })
                return Business.objects.filter(id=b.id)
            return qs
        return Business.objects.none()

    # Method: perform_create
    def perform_create(self, serializer):
        # We handle creation via service
        validated_data = serializer.validated_data
        BusinessRegistrationService.register_business(self.request.user, validated_data)

    # Method: create
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = BusinessRegistrationService.register_business(request.user, serializer.validated_data)
        return Response(self.get_serializer(business).data, status=status.HTTP_201_CREATED)

    # Method: update
    def update(self, request, *args, **kwargs):
        business = self.get_object()
        serializer = self.get_serializer(business, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        data = dict(serializer.validated_data)
        if request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN':
            if 'is_verified' in request.data:
                data['is_verified'] = str(request.data['is_verified']).lower() in ['true', '1', 'yes']
            if 'business_status' in request.data:
                data['business_status'] = request.data['business_status']

        updated_business = BusinessUpdateService.update_business(business, data)
        return Response(self.get_serializer(updated_business).data)

    # Method: destroy
    def destroy(self, request, *args, **kwargs):
        business = self.get_object()
        BusinessDeactivationService.deactivate_business(business)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    # Method: verify
    def verify(self, request, pk=None):
        business = self.get_object()
        BusinessVerificationService.verify_business(business)
        return Response({'status': 'Business verified'})

    @action(detail=True, methods=['get'])
    # Method: analytics
    def analytics(self, request, pk=None):
        business = self.get_object()
        stats = BusinessAnalyticsService.get_business_stats(business)
        return Response(stats)

# Class: BranchViewSet
class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated] # Additional permissions could be added

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Branch.objects.none()
        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return Branch.objects.all()
        return Branch.objects.filter(business__owner=user)

    # Method: perform_create
    def perform_create(self, serializer):
        business_id = self.request.data.get('business')
        business = BusinessRepository.get_by_id(business_id)
        BranchManagementService.add_branch(business, serializer.validated_data)

# Class: AddressViewSet
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Address.objects.none()
        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return Address.objects.all()
        return Address.objects.filter(business__owner=user)

    # Method: perform_create
    def perform_create(self, serializer):
        business_id = self.request.data.get('business')
        business = BusinessRepository.get_by_id(business_id)
        AddressManagementService.add_address(business, serializer.validated_data)

# Class: OperatingHoursViewSet
class OperatingHoursViewSet(viewsets.ModelViewSet):
    serializer_class = OperatingHoursSerializer
    permission_classes = [IsAuthenticated]

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return OperatingHours.objects.none()
        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return OperatingHours.objects.all()
        return OperatingHours.objects.filter(business__owner=user)

    # Method: create
    def create(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        business = BusinessRepository.get_by_id(business_id)
        hours_data = request.data.get('hours', [])
        hours_list = OperatingHoursService.set_operating_hours(business, hours_data)
        serializer = self.get_serializer(hours_list, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
