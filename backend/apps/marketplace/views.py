from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from .models import MarketplaceListing, MarketplaceOrder, MarketplaceOrderStatus, Wishlist, MarketplaceReview, ListingStatus
from .serializers import (
    MarketplaceListingReadSerializer, MarketplaceListingWriteSerializer,
    MarketplaceOrderSerializer, WishlistSerializer, MarketplaceReviewSerializer
)
from .services import ListingService, MarketplaceOrderService, RecommendationService
from .filters import MarketplaceListingFilter
from .permissions import HasMarketplacePermission


# Class: ListingViewSet
class ListingViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceListing.objects.filter(is_deleted=False)
    permission_classes = [HasMarketplacePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MarketplaceListingFilter
    search_fields = ['listing_title', 'product__name', 'product__category__name', 'business__name']
    ordering_fields = ['created_at', 'discounted_price', 'views', 'purchase_count']
    ordering = ['-created_at']

    # Method: get_queryset
    def get_queryset(self):
        from django.utils import timezone
        from .models import ListingStatus

        # Auto-release expired 15-minute pending order holds to return stock
        MarketplaceOrderService.release_expired_holds()

        # Auto-expire listings past their main expiration time limit
        MarketplaceListing.objects.filter(
            is_deleted=False,
            listing_status=ListingStatus.PUBLISHED,
            expires_at__lt=timezone.now()
        ).update(listing_status=ListingStatus.EXPIRED)

        qs = MarketplaceListing.objects.filter(is_deleted=False)
        user = self.request.user
        role = getattr(user, 'role', None)

        if not user.is_authenticated or role in ['CUSTOMER', 'NGO']:
            # Public / customer / NGO: show active listings from non-suspended/non-rejected businesses
            qs = qs.exclude(business__business_status__in=['SUSPENDED', 'REJECTED']).filter(
                listing_status=ListingStatus.PUBLISHED,
                quantity_available__gt=0,
                expires_at__gt=timezone.now(),
                business__is_active=True,
                business__is_verified=True,
                business__business_status='APPROVED'
            )
        elif role == 'VENDOR':
            # Vendors see only their own business listings
            try:
                qs = qs.filter(business__owner=user)
            except Exception:
                pass
        # ADMIN sees ALL listings (no filter applied)

        return qs

    # Method: get_serializer_class
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MarketplaceListingWriteSerializer
        return MarketplaceListingReadSerializer

    # Method: perform_destroy
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

    # Method: retrieve
    def retrieve(self, request, *args, **kwargs):
        # Record view metric
        response = super().retrieve(request, *args, **kwargs)
        ListingService.record_view(str(self.get_object().id))
        return response

    @action(detail=True, methods=['post'])
    # Method: publish
    def publish(self, request, pk=None):
        try:
            listing = ListingService.publish_listing(str(pk))
            return Response(self.get_serializer(listing).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: pause
    def pause(self, request, pk=None):
        try:
            listing = ListingService.pause_listing(str(pk))
            return Response(self.get_serializer(listing).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    # Method: close
    def close(self, request, pk=None):
        try:
            listing = ListingService.close_listing(str(pk))
            return Response(self.get_serializer(listing).data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='takedown')
    # Method: takedown
    def takedown(self, request, pk=None):
        """Admin-only: Unpublish a listing with a reason."""
        from django.utils import timezone
        listing = self.get_object()
        reason = request.data.get('reason', '')
        listing.listing_status = ListingStatus.UNPUBLISHED
        listing.takedown_reason = reason
        listing.takedown_at = timezone.now()
        listing.save(update_fields=['listing_status', 'takedown_reason', 'takedown_at', 'updated_at'])
        return Response({
            'detail': 'Listing taken down.',
            'listing_status': listing.listing_status,
            'takedown_reason': listing.takedown_reason,
            'takedown_at': listing.takedown_at,
        })

    @action(detail=True, methods=['post'], url_path='republish')
    # Method: republish
    def republish(self, request, pk=None):
        """Admin-only: Re-publish a taken-down listing and clear takedown metadata."""
        listing = self.get_object()
        listing.listing_status = ListingStatus.PUBLISHED
        listing.takedown_reason = None
        listing.takedown_at = None
        listing.save(update_fields=['listing_status', 'takedown_reason', 'takedown_at', 'updated_at'])
        return Response({'detail': 'Listing published.', 'listing_status': listing.listing_status})

    @action(detail=True, methods=['post'])
    # Method: add_to_wishlist
    def add_to_wishlist(self, request, pk=None):
        listing = self.get_object()
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, listing=listing
        )
        if created:
            return Response(WishlistSerializer(wishlist_item).data, status=status.HTTP_201_CREATED)
        # Already in wishlist — toggle off
        wishlist_item.delete()
        return Response({'detail': 'Removed from wishlist.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    # Method: recommendations
    def recommendations(self, request):
        customer_id = request.query_params.get('customer_id')
        listings = RecommendationService.get_ai_recommendations(customer_id)
        return Response(self.get_serializer(listings, many=True).data)


# Class: MarketplaceOrderViewSet
class MarketplaceOrderViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceOrder.objects.all()
    serializer_class = MarketplaceOrderSerializer
    permission_classes = [HasMarketplacePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'listing', 'customer']

    # Method: get_queryset
    def get_queryset(self):
        from django.db import models
        MarketplaceOrderService.release_expired_holds()
        user = self.request.user

        if not user.is_authenticated:
            return MarketplaceOrder.objects.none()

        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return MarketplaceOrder.objects.all()

        if getattr(user, 'role', '') == 'VENDOR':
            return MarketplaceOrder.objects.filter(
                models.Q(listing__business__owner=user) |
                models.Q(customer__email=user.email)
            )

        return MarketplaceOrder.objects.filter(customer__email=user.email)

    # Method: create
    def create(self, request, *args, **kwargs):
        try:
            from apps.orders.models import Customer
            listing_id = request.data.get('listing') or request.data.get('listing_id')
            listing = MarketplaceListing.objects.filter(id=listing_id).first()
            if not listing:
                return Response({'detail': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

            customer = None
            if request.user.is_authenticated:
                customer = Customer.objects.filter(user=request.user, business=listing.business).first()
                if not customer:
                    customer = Customer.objects.filter(email=request.user.email, business=listing.business).first()
                    if customer and not customer.user:
                        customer.user = request.user
                        customer.save(update_fields=['user'])
                if not customer:
                    customer = Customer.objects.create(
                        user=request.user,
                        business=listing.business,
                        first_name=request.user.first_name or "Customer",
                        last_name=request.user.last_name or "User",
                        email=request.user.email,
                    )
            elif request.data.get('customer'):
                customer = Customer.objects.filter(id=request.data.get('customer'), business=listing.business).first()

            if not customer:
                return Response({'detail': 'No valid customer profile available for this business.'}, status=status.HTTP_400_BAD_REQUEST)

            user_lat = request.data.get('user_lat') or request.data.get('latitude') or request.query_params.get('lat')
            user_lon = request.data.get('user_lon') or request.data.get('longitude') or request.query_params.get('lon')

            redeem_points = int(request.data.get('redeem_points', 0) or 0)

            order = MarketplaceOrderService.place_order(
                listing_id=listing_id,
                customer=customer,
                quantity=int(request.data.get('quantity', 1)),
                user=request.user,
                user_lat=user_lat,
                user_lon=user_lon,
                redeem_points=redeem_points
            )
            return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    # Method: verify_claim_code
    def verify_claim_code(self, request):
        from django.db import models
        claim_code = request.data.get('claim_code') or request.data.get('code')
        if not claim_code:
            return Response({'detail': 'Claim code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        clean_code = str(claim_code).replace('#', '').strip()
        user = request.user

        # Scope query strictly to orders belonging to this vendor's business(es)
        vendor_qs = MarketplaceOrder.objects.all()
        if not user.is_staff and getattr(user, 'role', '') != 'ADMIN':
            user_businesses = user.businesses.filter(is_deleted=False)
            vendor_qs = vendor_qs.filter(
                models.Q(listing__business__owner=user) |
                models.Q(listing__business__in=user_businesses)
            ).distinct()

        order = vendor_qs.filter(
            models.Q(linked_order__order_number__icontains=clean_code) |
            models.Q(id__icontains=clean_code)
        ).first()

        if not order:
            return Response({
                'detail': f'No pending order matching claim code #{clean_code} was found for your restaurant.'
            }, status=status.HTTP_404_NOT_FOUND)

        if order.status == MarketplaceOrderStatus.COMPLETED:
            return Response({
                'detail': f'Order matching claim code #{clean_code} has already been completed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if order.status == MarketplaceOrderStatus.CANCELLED:
            return Response({
                'detail': f'Order matching claim code #{clean_code} was cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = MarketplaceOrderStatus.COMPLETED
        order.save()

        if order.linked_order:
            from apps.orders.services import OrderService
            try:
                OrderService.complete_order(str(order.linked_order.id))
            except Exception:
                order.linked_order.order_status = 'COMPLETED'
                order.linked_order.save()
        elif order.customer:
            from apps.orders.repositories import CustomerRepository, LoyaltyTransactionRepository
            points_earned = max(1, int(order.total_price // 100))
            LoyaltyTransactionRepository.create({
                'customer': order.customer,
                'points': points_earned,
                'description': f"Earned from marketplace order #{str(order.id)[:8]}"
            })
            CustomerRepository.update(order.customer, {'loyalty_points': order.customer.loyalty_points + points_earned})

        listing = order.listing
        if listing and listing.quantity_available <= 0:
            listing.listing_status = ListingStatus.CLOSED
            listing.save(update_fields=['listing_status', 'updated_at'])

        if order.customer and getattr(order.customer.user, 'role', '') == 'NGO':
            from apps.donations.repositories import DonationImpactRepository
            from decimal import Decimal
            food_weight = Decimal(str(order.quantity)) * Decimal('0.5')
            DonationImpactRepository.create({
                'marketplace_order': order,
                'meals_served': order.quantity * 2,
                'food_saved_kg': food_weight,
                'carbon_saved_kg': food_weight * Decimal('2.5'),
                'beneficiaries': order.quantity
            })

        return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    # Method: complete
    def complete(self, request, pk=None):
        order = self.get_object()
        user = request.user
        if not user.is_staff and getattr(user, 'role', '') != 'ADMIN':
            user_businesses = user.businesses.filter(is_deleted=False)
            if order.listing.business.owner != user and order.listing.business not in user_businesses:
                return Response({'detail': 'You do not have permission to complete orders for another restaurant.'}, status=status.HTTP_403_FORBIDDEN)

        order.status = MarketplaceOrderStatus.COMPLETED
        order.save()
        if order.linked_order:
            from apps.orders.services import OrderService
            try:
                OrderService.complete_order(str(order.linked_order.id))
            except Exception:
                order.linked_order.order_status = 'COMPLETED'
                order.linked_order.save()
        elif order.customer:
            from apps.orders.repositories import CustomerRepository, LoyaltyTransactionRepository
            points_earned = max(1, int(order.total_price // 100))
            LoyaltyTransactionRepository.create({
                'customer': order.customer,
                'points': points_earned,
                'description': f"Earned from marketplace order #{str(order.id)[:8]}"
            })
            CustomerRepository.update(order.customer, {'loyalty_points': order.customer.loyalty_points + points_earned})

        listing = order.listing
        if listing and listing.quantity_available <= 0:
            listing.listing_status = ListingStatus.CLOSED
            listing.save(update_fields=['listing_status', 'updated_at'])

        if order.customer and getattr(order.customer.user, 'role', '') == 'NGO':
            from apps.donations.repositories import DonationImpactRepository
            from decimal import Decimal
            food_weight = Decimal(str(order.quantity)) * Decimal('0.5')
            DonationImpactRepository.create({
                'marketplace_order': order,
                'meals_served': order.quantity * 2,
                'food_saved_kg': food_weight,
                'carbon_saved_kg': food_weight * Decimal('2.5'),
                'beneficiaries': order.quantity
            })

        return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    # Method: cancel
    def cancel(self, request, pk=None):
        order = self.get_object()
        user = request.user
        if not user.is_staff and getattr(user, 'role', '') != 'ADMIN':
            user_businesses = user.businesses.filter(is_deleted=False)
            if order.listing.business.owner != user and order.listing.business not in user_businesses:
                return Response({'detail': 'You do not have permission to cancel orders for another restaurant.'}, status=status.HTTP_403_FORBIDDEN)

        order.status = MarketplaceOrderStatus.CANCELLED
        order.save()
        if order.linked_order:
            order.linked_order.order_status = 'CANCELLED'
            order.linked_order.save()
        listing = order.listing
        if listing:
            listing.quantity_available += order.quantity
            if listing.listing_status in [ListingStatus.PAUSED, ListingStatus.CLOSED, ListingStatus.EXPIRED]:
                listing.listing_status = ListingStatus.PUBLISHED
            listing.save()
        return Response(self.get_serializer(order).data, status=status.HTTP_200_OK)


# Class: WishlistViewSet
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [HasMarketplacePermission]

    # Method: get_queryset
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related(
            'listing',
            'listing__product',
            'listing__product__category',
            'listing__business',
        ).order_by('-created_at')

    # Method: perform_create
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Class: MarketplaceReviewViewSet
class MarketplaceReviewViewSet(viewsets.ModelViewSet):
    queryset = MarketplaceReview.objects.all()
    serializer_class = MarketplaceReviewSerializer
    permission_classes = [HasMarketplacePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['listing', 'customer', 'rating']

    # Method: perform_create
    def perform_create(self, serializer):
        listing = serializer.validated_data['listing']
        user = self.request.user
        
        from apps.orders.models import Customer
        customer = Customer.objects.filter(user=user, business=listing.business).first()
        if not customer:
            customer = Customer.objects.filter(email=user.email, business=listing.business).first()

        if not customer:
            raise ValidationError("You can only review listings you've completed an order for.")

        has_completed_order = MarketplaceOrder.objects.filter(
            listing=listing,
            customer=customer,
            status=MarketplaceOrderStatus.COMPLETED
        ).exists()

        if not has_completed_order:
            raise ValidationError("You can only review listings you've completed an order for.")

        serializer.save(customer=customer)
