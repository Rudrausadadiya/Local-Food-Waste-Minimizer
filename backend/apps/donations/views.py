from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from .models import (
    NGO, DonationListing, DonationRequest, DonationPickup, 
    DonationImpact, PickupRoute
)
from .serializers import (
    NGOSerializer, DonationListingSerializer, DonationRequestSerializer,
    DonationPickupSerializer, DonationImpactSerializer, PickupRouteSerializer
)
from .services import NGOService, DonationService, MatchingService
from .filters import DonationListingFilter
from .permissions import HasDonationPermission

class NGOViewSet(viewsets.ModelViewSet):
    queryset = NGO.objects.all()
    serializer_class = NGOSerializer
    permission_classes = [HasDonationPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['verification_status', 'is_active']
    search_fields = ['organization_name', 'registration_number', 'email']

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        try:
            ngo = NGOService.verify_ngo(str(pk), admin_user=request.user)
            return Response(self.get_serializer(ngo).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DonationListingViewSet(viewsets.ModelViewSet):
    queryset = DonationListing.objects.filter(is_deleted=False)
    serializer_class = DonationListingSerializer
    permission_classes = [HasDonationPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DonationListingFilter
    search_fields = ['product__name', 'business__name']
    ordering_fields = ['created_at', 'available_until', 'priority']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def convert_marketplace(self, request):
        try:
            listing = DonationService.convert_from_marketplace(
                request.data.get('marketplace_listing_id'), 
                user=request.user
            )
            return Response(self.get_serializer(listing).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def match_ngos(self, request):
        lat = float(request.query_params.get('lat', 0.0))
        lon = float(request.query_params.get('lon', 0.0))
        ngos = MatchingService.get_nearby_ngos(lat, lon)
        return Response(NGOSerializer(ngos, many=True).data)


class DonationRequestViewSet(viewsets.ModelViewSet):
    queryset = DonationRequest.objects.all()
    serializer_class = DonationRequestSerializer
    permission_classes = [HasDonationPermission]

    def create(self, request, *args, **kwargs):
        try:
            ngo_id = request.data.get('ngo')
            ngo = NGO.objects.get(id=ngo_id)
            req = DonationService.request_donation(
                listing_id=request.data.get('donation_listing'),
                ngo=ngo,
                requested_quantity=int(request.data.get('requested_quantity'))
            )
            return Response(self.get_serializer(req).data, status=status.HTTP_201_CREATED)
        except (ValidationError, NGO.DoesNotExist) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            req = DonationService.approve_request(
                request_id=str(pk),
                approved_quantity=int(request.data.get('approved_quantity')),
                user=request.user
            )
            return Response(self.get_serializer(req).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DonationPickupViewSet(viewsets.ModelViewSet):
    queryset = DonationPickup.objects.all()
    serializer_class = DonationPickupSerializer
    permission_classes = [HasDonationPermission]

    def create(self, request, *args, **kwargs):
        try:
            pickup = DonationService.schedule_pickup(
                request_id=request.data.get('donation_request'),
                pickup_time=request.data.get('pickup_time')
            )
            return Response(self.get_serializer(pickup).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            pickup = DonationService.confirm_pickup(str(pk), user=request.user)
            return Response(self.get_serializer(pickup).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
