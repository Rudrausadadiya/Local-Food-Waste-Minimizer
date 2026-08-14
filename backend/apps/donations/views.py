from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Count

from .models import (
    NGO, DonationListing, DonationRequest, DonationPickup, DonationImpact, PickupRoute
)
from .serializers import (
    NGOSerializer, DonationListingSerializer, DonationRequestSerializer,
    DonationPickupSerializer, DonationImpactSerializer, PickupRouteSerializer
)
from .services import NGOService, DonationService, MatchingService, PickupRouteService
from .filters import DonationListingFilter
from .permissions import HasDonationPermission

# Class: NGOViewSet
class NGOViewSet(viewsets.ModelViewSet):
    serializer_class = NGOSerializer
    permission_classes = [HasDonationPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['verification_status', 'is_active']
    search_fields = ['organization_name', 'registration_number', 'email']

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return NGO.objects.none()
        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return NGO.objects.all()
        if getattr(user, 'role', '') == 'NGO':
            return NGO.objects.filter(user=user)
        return NGO.objects.none()

    @action(detail=True, methods=['post'])
    # Method: verify
    def verify(self, request, pk=None):
        try:
            ngo = NGOService.verify_ngo(str(pk), admin_user=request.user)
            return Response(self.get_serializer(ngo).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Class: DonationListingViewSet
class DonationListingViewSet(viewsets.ModelViewSet):
    queryset = DonationListing.objects.filter(is_deleted=False)
    serializer_class = DonationListingSerializer
    permission_classes = [HasDonationPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DonationListingFilter
    search_fields = ['product__name', 'business__name']
    ordering_fields = ['created_at', 'available_until', 'priority']
    ordering = ['-created_at']

    # Method: get_queryset
    def get_queryset(self):
        qs = DonationListing.objects.filter(is_deleted=False)
        user = self.request.user
        if not user.is_authenticated:
            return DonationListing.objects.none()

        role = getattr(user, 'role', '')
        if user.is_staff or role == 'ADMIN':
            return qs

        if role == 'VENDOR':
            user_businesses = user.businesses.filter(is_deleted=False)
            return qs.filter(
                models.Q(business__owner=user) |
                models.Q(business__in=user_businesses)
            ).distinct()

        if role == 'NGO':
            return qs.filter(
                business__is_active=True,
                business__is_verified=True,
                business__business_status='APPROVED'
            ).exclude(business__business_status__in=['SUSPENDED', 'REJECTED'])

        return qs.none()

    @action(detail=False, methods=['post'])
    # Method: convert_marketplace
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
    # Method: match_ngos
    def match_ngos(self, request):
        lat = float(request.query_params.get('lat', 0.0))
        lon = float(request.query_params.get('lon', 0.0))
        ngos = MatchingService.get_nearby_ngos(lat, lon)
        return Response(NGOSerializer(ngos, many=True).data)


# Class: DonationRequestViewSet
class DonationRequestViewSet(viewsets.ModelViewSet):
    queryset = DonationRequest.objects.all()
    serializer_class = DonationRequestSerializer
    permission_classes = [HasDonationPermission]

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return DonationRequest.objects.none()

        role = getattr(user, 'role', '')
        if user.is_staff or role == 'ADMIN':
            return DonationRequest.objects.all()

        if role == 'NGO':
            ngo = getattr(user, 'ngo_profile', None)
            if not ngo:
                return DonationRequest.objects.filter(ngo__user=user)
            return DonationRequest.objects.filter(ngo=ngo)

        if role == 'VENDOR':
            user_businesses = user.businesses.filter(is_deleted=False)
            return DonationRequest.objects.filter(
                models.Q(donation_listing__business__owner=user) |
                models.Q(donation_listing__business__in=user_businesses)
            ).distinct()

        return DonationRequest.objects.none()

    # Method: create
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            ngo = None
            if getattr(user, 'role', '') == 'NGO':
                ngo = getattr(user, 'ngo_profile', None)
                if not ngo:
                    ngo = NGO.objects.filter(user=user).first()
            
            if not ngo:
                ngo_id = request.data.get('ngo')
                if ngo_id:
                    ngo = NGO.objects.filter(id=ngo_id).first()

            if not ngo:
                return Response({'detail': 'No valid NGO profile found for your account.'}, status=status.HTTP_400_BAD_REQUEST)

            # Prevent NGO from creating request under another NGO's identity
            if getattr(user, 'role', '') == 'NGO' and ngo.user != user:
                return Response({'detail': 'You cannot request donations on behalf of another NGO.'}, status=status.HTTP_403_FORBIDDEN)

            req = DonationService.request_donation(
                listing_id=request.data.get('donation_listing'),
                ngo=ngo,
                requested_quantity=int(request.data.get('requested_quantity', 1))
            )
            return Response(self.get_serializer(req).data, status=status.HTTP_201_CREATED)
        except (ValidationError, NGO.DoesNotExist) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: approve
    def approve(self, request, pk=None):
        try:
            req_obj = self.get_object()
            user = request.user
            if not user.is_staff and getattr(user, 'role', '') != 'ADMIN':
                user_businesses = user.businesses.filter(is_deleted=False)
                biz = req_obj.donation_listing.business
                if biz.owner != user and biz not in user_businesses:
                    return Response({'detail': 'You do not have permission to approve donation requests for another restaurant.'}, status=status.HTTP_403_FORBIDDEN)

            req = DonationService.approve_request(
                request_id=str(pk),
                approved_quantity=int(request.data.get('approved_quantity', req_obj.requested_quantity)),
                user=user
            )
            return Response(self.get_serializer(req).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Class: DonationPickupViewSet
class DonationPickupViewSet(viewsets.ModelViewSet):
    queryset = DonationPickup.objects.all()
    serializer_class = DonationPickupSerializer
    permission_classes = [HasDonationPermission]

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return DonationPickup.objects.none()

        role = getattr(user, 'role', '')
        if user.is_staff or role == 'ADMIN':
            return DonationPickup.objects.all()

        if role == 'NGO':
            ngo = getattr(user, 'ngo_profile', None)
            if not ngo:
                return DonationPickup.objects.filter(donation_request__ngo__user=user)
            return DonationPickup.objects.filter(donation_request__ngo=ngo)

        if role == 'VENDOR':
            user_businesses = user.businesses.filter(is_deleted=False)
            return DonationPickup.objects.filter(
                models.Q(donation_request__donation_listing__business__owner=user) |
                models.Q(donation_request__donation_listing__business__in=user_businesses)
            ).distinct()

        return DonationPickup.objects.none()

    # Method: create
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
    # Method: confirm
    def confirm(self, request, pk=None):
        try:
            pickup_obj = self.get_object()
            user = request.user
            if not user.is_staff and getattr(user, 'role', '') != 'ADMIN':
                role = getattr(user, 'role', '')
                req = pickup_obj.donation_request
                if role == 'NGO':
                    ngo = getattr(user, 'ngo_profile', None)
                    if req.ngo.user != user and (ngo and req.ngo != ngo):
                        return Response({'detail': 'You do not have permission to confirm pickups for another NGO.'}, status=status.HTTP_403_FORBIDDEN)
                elif role == 'VENDOR':
                    user_businesses = user.businesses.filter(is_deleted=False)
                    biz = req.donation_listing.business
                    if biz.owner != user and biz not in user_businesses:
                        return Response({'detail': 'You do not have permission to confirm pickups for another restaurant.'}, status=status.HTTP_403_FORBIDDEN)

            pickup = DonationService.confirm_pickup(str(pk), user=user)
            return Response(self.get_serializer(pickup).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Class: NGOImpactSummaryView
class NGOImpactSummaryView(APIView):
    permission_classes = [HasDonationPermission]

    # Method: get
    def get(self, request):
        role = getattr(request.user, 'role', None)
        if role == 'ADMIN' or request.user.is_staff:
            qs = DonationImpact.objects.all()
        elif role == 'NGO':
            ngo = getattr(request.user, 'ngo_profile', None)
            if not ngo:
                return Response({'detail': 'No NGO profile found.'}, status=status.HTTP_403_FORBIDDEN)
            from django.db.models import Q
            qs = DonationImpact.objects.filter(
                Q(donation_pickup__donation_request__ngo=ngo) | 
                Q(marketplace_order__customer__user__ngo_profile=ngo)
            )
        else:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)

        totals = qs.aggregate(
            total_meals=Sum('meals_served'),
            total_food_kg=Sum('food_saved_kg'),
            total_carbon_kg=Sum('carbon_saved_kg'),
            total_beneficiaries=Sum('beneficiaries'),
            pickup_count=Count('id'),
        )
        return Response({
            'meals_served': totals['total_meals'] or 0,
            'food_saved_kg': float(totals['total_food_kg'] or 0),
            'carbon_saved_kg': float(totals['total_carbon_kg'] or 0),
            'beneficiaries': totals['total_beneficiaries'] or 0,
            'completed_pickups': totals['pickup_count'] or 0,
        })


# Class: DonationImpactViewSet
class DonationImpactViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationImpactSerializer
    permission_classes = [HasDonationPermission]

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return DonationImpact.objects.none()
        role = getattr(user, 'role', '')
        if user.is_staff or role == 'ADMIN':
            return DonationImpact.objects.all().select_related(
                'donation_pickup',
                'donation_pickup__donation_request',
                'donation_pickup__donation_request__ngo',
                'donation_pickup__donation_request__donation_listing',
                'marketplace_order',
                'marketplace_order__customer'
            )
        if role == 'NGO':
            ngo = getattr(user, 'ngo_profile', None)
            if not ngo:
                return DonationImpact.objects.none()
            from django.db.models import Q
            return DonationImpact.objects.filter(
                Q(donation_pickup__donation_request__ngo=ngo) |
                Q(marketplace_order__customer__user__ngo_profile=ngo)
            ).select_related(
                'donation_pickup',
                'donation_pickup__donation_request',
                'donation_pickup__donation_request__ngo',
                'donation_pickup__donation_request__donation_listing',
                'marketplace_order',
                'marketplace_order__customer'
            )
        return DonationImpact.objects.none()


# Class: PickupRouteViewSet
class PickupRouteViewSet(viewsets.ModelViewSet):
    serializer_class = PickupRouteSerializer
    permission_classes = [HasDonationPermission]

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return PickupRoute.objects.none()
        role = getattr(user, 'role', '')
        if user.is_staff or role == 'ADMIN':
            return PickupRoute.objects.all().prefetch_related('pickups', 'marketplace_orders')
        if role == 'NGO':
            ngo = getattr(user, 'ngo_profile', None)
            if not ngo:
                return PickupRoute.objects.none()
            return PickupRoute.objects.filter(ngo=ngo).prefetch_related('pickups', 'marketplace_orders')
        return PickupRoute.objects.none()

    # Method: create
    def create(self, request, *args, **kwargs):
        role = getattr(request.user, 'role', None)
        if role != 'NGO':
            return Response({'detail': 'Only NGOs can create pickup routes.'}, status=status.HTTP_403_FORBIDDEN)
        ngo = getattr(request.user, 'ngo_profile', None)
        if not ngo:
            return Response({'detail': 'No NGO profile found.'}, status=status.HTTP_403_FORBIDDEN)

        pickup_ids = request.data.get('pickup_ids', [])
        route_date = request.data.get('route_date')
        driver_name = request.data.get('driver_name', '')

        if not pickup_ids or not route_date:
            return Response({'detail': 'pickup_ids and route_date are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            route = PickupRouteService.create_route(
                ngo=ngo,
                pickup_ids=pickup_ids,
                route_date=route_date,
                driver_name=driver_name
            )
            return Response(self.get_serializer(route).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


