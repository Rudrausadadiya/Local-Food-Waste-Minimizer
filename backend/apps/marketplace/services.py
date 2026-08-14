import uuid
from typing import Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import MarketplaceListing, ListingStatus, MarketplaceOrder, MarketplaceOrderStatus
from .repositories import (
    MarketplaceListingRepository, MarketplaceOrderRepository, 
    WishlistRepository
)
from .validators import validate_business_active, validate_inventory_for_listing, validate_inventory_batch
from .signals import (
    listing_created, listing_published, listing_sold, 
    listing_expired, listing_removed, listing_viewed, 
    listing_added_to_wishlist, listing_price_changed
)
from apps.orders.services import OrderService


# Class: ListingService
class ListingService:
    @staticmethod
    @transaction.atomic
    # Method: create_listing
    def create_listing(data: Dict[str, Any], user=None) -> MarketplaceListing:
        validate_inventory_for_listing(data['product'], data.get('quantity_available', 0), str(data['branch'].id))
        
        if 'inventory_batch' in data and data['inventory_batch']:
            validate_inventory_batch(data['inventory_batch'])
            
        data['created_by'] = user
        listing = MarketplaceListingRepository.create(data)
        
        listing_created.send(sender=ListingService, listing=listing)
        return listing

    @staticmethod
    @transaction.atomic
    # Method: update_listing
    def update_listing(listing_id: str, data: Dict[str, Any], user=None) -> MarketplaceListing:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if not listing:
            raise ValidationError("Listing not found.")
            
        if 'quantity_available' in data:
            validate_inventory_for_listing(listing.product, data['quantity_available'], str(listing.branch.id))
            
        if 'inventory_batch' in data and data['inventory_batch']:
            validate_inventory_batch(data['inventory_batch'])

        price_changed = False
        if 'discounted_price' in data and Decimal(str(data['discounted_price'])) != listing.discounted_price:
            price_changed = True

        listing = MarketplaceListingRepository.update(listing, data)
        
        if price_changed:
            listing_price_changed.send(sender=ListingService, listing=listing)
            
        ListingService.sync_inventory_state(str(listing.id))
        
        return listing

    @staticmethod
    @transaction.atomic
    # Method: publish_listing
    def publish_listing(listing_id: str) -> MarketplaceListing:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if not listing:
            raise ValidationError("Listing not found.")
            
        validate_business_active(listing.business)
        validate_inventory_for_listing(listing.product, listing.quantity_available, str(listing.branch.id))
        
        if listing.inventory_batch:
            validate_inventory_batch(listing.inventory_batch)

        listing = MarketplaceListingRepository.update(listing, {'listing_status': ListingStatus.PUBLISHED})
        listing_published.send(sender=ListingService, listing=listing)
        return listing

    @staticmethod
    @transaction.atomic
    # Method: pause_listing
    def pause_listing(listing_id: str) -> MarketplaceListing:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if listing:
            return MarketplaceListingRepository.update(listing, {'listing_status': ListingStatus.PAUSED})
        raise ValidationError("Listing not found.")

    @staticmethod
    @transaction.atomic
    # Method: close_listing
    def close_listing(listing_id: str) -> MarketplaceListing:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if listing:
            listing = MarketplaceListingRepository.update(listing, {'listing_status': ListingStatus.CLOSED})
            listing_removed.send(sender=ListingService, listing=listing)
            return listing
        raise ValidationError("Listing not found.")

    @staticmethod
    # Method: record_view
    def record_view(listing_id: str) -> None:
        listing = MarketplaceListingRepository.get_by_id(listing_id)
        if listing:
            MarketplaceListingRepository.increment_metric(listing, 'views')
            listing_viewed.send(sender=ListingService, listing=listing)

    @staticmethod
    @transaction.atomic
    # Method: add_to_wishlist
    def add_to_wishlist(listing_id: str, customer) -> Any:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if not listing:
            raise ValidationError("Listing not found.")
            
        wishlist = WishlistRepository.create({
            'customer': customer,
            'listing': listing
        })
        
        MarketplaceListingRepository.increment_metric(listing, 'wishlist_count')
        listing_added_to_wishlist.send(sender=ListingService, listing=listing, customer=customer)
        return wishlist

    @staticmethod
    @transaction.atomic
    # Method: sync_inventory_state
    def sync_inventory_state(listing_id: str) -> None:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if not listing:
            return
            
        should_deactivate = False
        if listing.quantity_available <= 0:
            should_deactivate = True
            
        if listing.inventory_batch and listing.inventory_batch.expiry_date and listing.inventory_batch.expiry_date < timezone.now().date():
            should_deactivate = True
            
        if should_deactivate and listing.listing_status == ListingStatus.PUBLISHED:
            listing = MarketplaceListingRepository.update(listing, {'listing_status': ListingStatus.EXPIRED})
            listing_expired.send(sender=ListingService, listing=listing)


# Class: MarketplaceOrderService
class MarketplaceOrderService:
    @staticmethod
    @transaction.atomic
    # Method: release_expired_holds
    def release_expired_holds():
        now = timezone.now()
        expired_orders = MarketplaceOrder.objects.select_for_update().filter(
            status=MarketplaceOrderStatus.PENDING,
            claim_expires_at__lt=now
        )
        for order in expired_orders:
            order.status = MarketplaceOrderStatus.CANCELLED
            order.save()
            
            if order.linked_order:
                order.linked_order.order_status = 'CANCELLED'
                order.linked_order.save()
                
            # Restore stock back to the listing
            listing = order.listing
            listing.quantity_available += order.quantity
            if listing.listing_status in [ListingStatus.PAUSED, ListingStatus.CLOSED, ListingStatus.EXPIRED]:
                # If listing is not past its main expiration date, re-publish it
                if not listing.expires_at or listing.expires_at > now:
                    listing.listing_status = ListingStatus.PUBLISHED
            listing.save()

    @staticmethod
    @transaction.atomic
    # Method: place_order
    def place_order(listing_id: str, customer, quantity: int, user=None, user_lat=None, user_lon=None, redeem_points: int = 0) -> MarketplaceOrder:
        # First release any expired holds across the system to free up held stock
        MarketplaceOrderService.release_expired_holds()

        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if not listing:
            raise ValidationError("Listing not found.")

        is_ngo = user and getattr(user, 'role', '') == 'NGO'

        if not is_ngo:
            # Validate 15 km distance radius between user and store location
            if user_lat is None or user_lon is None:
                raise ValidationError("We need your location to verify you are within the 15km reservation radius. Please allow location access in your browser.")
                
            from common.utils import get_branch_coordinates, validate_15km_radius
            target_lat, target_lon = get_branch_coordinates(listing.branch)
            validate_15km_radius(user_lat, user_lon, target_lat, target_lon, entity_name="surplus food")
            
        if listing.expires_at and listing.expires_at < timezone.now():
            listing.listing_status = ListingStatus.EXPIRED
            listing.save()
            raise ValidationError("This surplus food listing has expired and is no longer available.")

        if listing.listing_status != ListingStatus.PUBLISHED:
            raise ValidationError("Listing is currently sold out or unavailable for purchase.")
            
        if quantity > listing.quantity_available:
            raise ValidationError("Requested quantity exceeds listing availability.")

        # Prevent user from placing multiple active 15-minute pending holds on the same listing
        from django.db import models
        existing_hold = MarketplaceOrder.objects.filter(
            listing=listing,
            status=MarketplaceOrderStatus.PENDING,
            claim_expires_at__gt=timezone.now()
        )
        if user and user.is_authenticated:
            existing_hold = existing_hold.filter(
                models.Q(customer__user=user) | models.Q(customer__email=user.email)
            )
        else:
            existing_hold = existing_hold.filter(customer=customer)

        if existing_hold.exists():
            raise ValidationError("You already have an active 15-minute reservation hold for this item. Please complete pickup or wait for your hold to expire before reserving again.")
            
        total_price = listing.discounted_price * Decimal(str(quantity))

        # Handle loyalty points redemption
        if redeem_points > 0:
            if not customer:
                raise ValidationError("Customer required to redeem loyalty points.")
            if redeem_points > customer.loyalty_points:
                raise ValidationError(f"Cannot redeem {redeem_points} points; customer only has {customer.loyalty_points} points available.")

            from apps.orders.repositories import CustomerRepository, LoyaltyTransactionRepository
            CustomerRepository.update(customer, {'loyalty_points': customer.loyalty_points - redeem_points})
            LoyaltyTransactionRepository.create({
                'customer': customer,
                'points': -redeem_points,
                'description': f"Redeemed {redeem_points} points discount on surplus reservation"
            })
            total_price = max(Decimal('0.00'), total_price - Decimal(str(redeem_points)))
        
        # Build Standard Order using OrderService
        order_data = {
            'business': listing.business,
            'branch': listing.branch,
            'customer': customer,
            'order_number': f"MKT-{listing.id.hex[:8].upper()}-{uuid.uuid4().hex[:6].upper()}",
            'created_by': user,
            'order_type': 'ONLINE'
        }
        
        items_payload = [{
            'product': listing.product,
            'quantity': quantity,
            'unit_price': listing.discounted_price
        }]
        
        main_order = OrderService.create_order(order_data, items_payload)
        
        # Create Marketplace Order wrapper with 15-minute claim holding window
        from datetime import timedelta
        claim_expires_at = timezone.now() + timedelta(minutes=15)

        mp_order = MarketplaceOrderRepository.create({
            'listing': listing,
            'customer': customer,
            'quantity': quantity,
            'total_price': total_price,
            'linked_order': main_order,
            'claim_expires_at': claim_expires_at,
            'status': MarketplaceOrderStatus.PENDING
        })
        
        # Update Listing Quantity & Metrics
        MarketplaceListingRepository.increment_metric(listing, 'purchase_count')
        listing.quantity_available -= quantity
        if listing.quantity_available <= 0:
            listing.listing_status = ListingStatus.PAUSED
        listing.save()
        
        ListingService.sync_inventory_state(str(listing.id))
        
        listing_sold.send(sender=MarketplaceOrderService, listing=listing, order=mp_order)
        return mp_order


# Class: RecommendationService
class RecommendationService:
    @staticmethod
    # Method: get_ai_recommendations
    def get_ai_recommendations(customer_id: str, limit: int = 10) -> List[MarketplaceListing]:
        """
        Implementation ready for AI models. 
        Currently falls back to popularity heuristic.
        """
        return list(MarketplaceListing.objects.filter(
            listing_status=ListingStatus.PUBLISHED,
            is_deleted=False
        ).order_by('-purchase_count', '-views', '-created_at')[:limit])
