from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Business, Branch, Address, OperatingHours
from .serializers import BusinessSerializer, BranchSerializer, AddressSerializer, OperatingHoursSerializer
from .repositories import BusinessRepository, BranchRepository, AddressRepository, OperatingHoursRepository
from .services import (
    BusinessRegistrationService, BusinessUpdateService, BusinessVerificationService,
    BusinessDeactivationService, BranchManagementService, AddressManagementService,
    OperatingHoursService, BusinessAnalyticsService
)
from .permissions import IsBusinessOwner, CustomerCannotCreateBusiness

class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsBusinessOwner, CustomerCannotCreateBusiness]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business_type', 'business_status', 'is_verified', 'is_active']
    search_fields = ['business_name', 'business_email', 'business_phone', 'description']
    ordering_fields = ['created_at', 'business_name', 'average_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return BusinessRepository.get_all_active()

    def perform_create(self, serializer):
        # We handle creation via service
        validated_data = serializer.validated_data
        BusinessRegistrationService.register_business(self.request.user, validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = BusinessRegistrationService.register_business(request.user, serializer.validated_data)
        return Response(self.get_serializer(business).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        business = self.get_object()
        serializer = self.get_serializer(business, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        updated_business = BusinessUpdateService.update_business(business, serializer.validated_data)
        return Response(self.get_serializer(updated_business).data)

    def destroy(self, request, *args, **kwargs):
        business = self.get_object()
        BusinessDeactivationService.deactivate_business(business)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        business = self.get_object()
        BusinessVerificationService.verify_business(business)
        return Response({'status': 'Business verified'})

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        business = self.get_object()
        stats = BusinessAnalyticsService.get_business_stats(business)
        return Response(stats)

class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated] # Additional permissions could be added

    def get_queryset(self):
        # Optionally filter by business ID if nested routing is used
        business_id = self.request.query_params.get('business_id')
        if business_id:
            return BranchRepository.get_by_business(business_id)
        return Branch.objects.all()

    def perform_create(self, serializer):
        business_id = self.request.data.get('business')
        business = BusinessRepository.get_by_id(business_id)
        BranchManagementService.add_branch(business, serializer.validated_data)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        business_id = self.request.query_params.get('business_id')
        if business_id:
            return AddressRepository.get_by_business(business_id)
        return Address.objects.all()

    def perform_create(self, serializer):
        business_id = self.request.data.get('business')
        business = BusinessRepository.get_by_id(business_id)
        AddressManagementService.add_address(business, serializer.validated_data)

class OperatingHoursViewSet(viewsets.ModelViewSet):
    serializer_class = OperatingHoursSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        business_id = self.request.query_params.get('business_id')
        if business_id:
            return OperatingHoursRepository.get_by_business(business_id)
        return OperatingHours.objects.all()

    def create(self, request, *args, **kwargs):
        business_id = request.data.get('business_id')
        business = BusinessRepository.get_by_id(business_id)
        hours_data = request.data.get('hours', [])
        hours_list = OperatingHoursService.set_operating_hours(business, hours_data)
        serializer = self.get_serializer(hours_list, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
