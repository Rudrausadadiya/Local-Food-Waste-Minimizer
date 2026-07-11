from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from .models import MarketplaceListing, MarketplaceOrder, Wishlist, MarketplaceReview
from .serializers import (
    MarketplaceListingReadSerializer, MarketplaceListingWriteSerializer,
    MarketplaceOrderSerializer, WishlistSerializer, MarketplaceReviewSerializer
)
from .services import ListingService, MarketplaceOrderService, RecommendationService
from .filters import MarketplaceListingFilter
from .permissions import HasMarketplacePermission

class ListingViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceListing.objects.filter(is_deleted=False)
    permission_classes = [HasMarketplacePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MarketplaceListingFilter
    search_fields = ['listing_title', 'product__name', 'product__category__name', 'business__name']
    ordering_fields = ['created_at', 'discounted_price', 'views', 'purchase_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MarketplaceListingWriteSerializer
        return MarketplaceListingReadSerializer

    def retrieve(self, request, *args, **kwargs):
        # Record view metric
        response = super().retrieve(request, *args, **kwargs)
        ListingService.record_view(str(self.get_object().id))
        return response

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        try:
            listing = ListingService.publish_listing(str(pk))
            return Response(self.get_serializer(listing).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        try:
            listing = ListingService.pause_listing(str(pk))
            return Response(self.get_serializer(listing).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        try:
            listing = ListingService.close_listing(str(pk))
            return Response(self.get_serializer(listing).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        try:
            # Assuming customer profile is linked to request.user
            customer = request.user.customer_profile if hasattr(request.user, 'customer_profile') else None
            if not customer:
                return Response({'detail': "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)
                
            wishlist = ListingService.add_to_wishlist(str(pk), customer)
            return Response(WishlistSerializer(wishlist).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        customer_id = request.query_params.get('customer_id')
        listings = RecommendationService.get_ai_recommendations(customer_id)
        return Response(self.get_serializer(listings, many=True).data)


class MarketplaceOrderViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceOrder.objects.all()
    serializer_class = MarketplaceOrderSerializer
    permission_classes = [HasMarketplacePermission]

    def create(self, request, *args, **kwargs):
        try:
            customer = request.user.customer_profile if hasattr(request.user, 'customer_profile') else None
            if not customer:
                # If they pass it explicitly
                customer_id = request.data.get('customer')
                from apps.orders.models import Customer
                customer = Customer.objects.get(id=customer_id)
                
            order = MarketplaceOrderService.place_order(
                listing_id=request.data.get('listing'),
                customer=customer,
                quantity=int(request.data.get('quantity', 1)),
                user=request.user
            )
            return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)
        except (ValidationError, Exception) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [HasMarketplacePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer']


class MarketplaceReviewViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceReview.objects.all()
    serializer_class = MarketplaceReviewSerializer
    permission_classes = [HasMarketplacePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['listing', 'customer', 'rating']
