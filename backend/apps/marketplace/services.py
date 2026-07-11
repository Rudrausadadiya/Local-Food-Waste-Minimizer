from typing import Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import MarketplaceListing, ListingStatus, MarketplaceOrder, MarketplaceOrderStatus
from .repositories import (
    MarketplaceListingRepository, MarketplaceOrderRepository, 
    WishlistRepository, MarketplaceReviewRepository
)
from .validators import validate_business_active, validate_inventory_for_listing, validate_inventory_batch
from .signals import (
    listing_created, listing_published, listing_sold, 
    listing_expired, listing_removed, listing_viewed, 
    listing_added_to_wishlist, listing_price_changed
)
from apps.inventory.services import InventoryService
from apps.orders.services import OrderService


class ListingService:
    @staticmethod
    @transaction.atomic
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
    def pause_listing(listing_id: str) -> MarketplaceListing:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if listing:
            return MarketplaceListingRepository.update(listing, {'listing_status': ListingStatus.PAUSED})
        raise ValidationError("Listing not found.")

    @staticmethod
    @transaction.atomic
    def close_listing(listing_id: str) -> MarketplaceListing:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if listing:
            listing = MarketplaceListingRepository.update(listing, {'listing_status': ListingStatus.CLOSED})
            listing_removed.send(sender=ListingService, listing=listing)
            return listing
        raise ValidationError("Listing not found.")

    @staticmethod
    def record_view(listing_id: str) -> None:
        listing = MarketplaceListingRepository.get_by_id(listing_id)
        if listing:
            MarketplaceListingRepository.increment_metric(listing, 'views')
            listing_viewed.send(sender=ListingService, listing=listing)

    @staticmethod
    @transaction.atomic
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


class MarketplaceOrderService:
    @staticmethod
    @transaction.atomic
    def place_order(listing_id: str, customer, quantity: int, user=None) -> MarketplaceOrder:
        listing = MarketplaceListingRepository.get_by_id_for_update(listing_id)
        if not listing:
            raise ValidationError("Listing not found.")
            
        if listing.listing_status != ListingStatus.PUBLISHED:
            raise ValidationError("Listing is not available for purchase.")
            
        if quantity > listing.quantity_available:
            raise ValidationError("Requested quantity exceeds listing availability.")
            
        total_price = listing.discounted_price * Decimal(str(quantity))
        
        # Build Standard Order using OrderService
        order_data = {
            'business': listing.business,
            'branch': listing.branch,
            'customer': customer,
            'order_number': f"MKT-{listing.id.hex[:8].upper()}-{timezone.now().strftime('%M%S')}",
            'created_by': user,
            'order_type': 'ONLINE'
        }
        
        items_payload = [{
            'product': listing.product,
            'quantity': quantity,
            'unit_price': listing.discounted_price
        }]
        
        # create_order will inherently call InventoryService.reserve_stock for the standard Order system
        main_order = OrderService.create_order(order_data, items_payload)
        
        # Create Marketplace Order wrapper
        mp_order = MarketplaceOrderRepository.create({
            'listing': listing,
            'customer': customer,
            'quantity': quantity,
            'total_price': total_price,
            'linked_order': main_order,
            'status': MarketplaceOrderStatus.COMPLETED  # Assume immediate completion for marketplace cart flow, or handle payment via linked_order
        })
        
        # Update Listing Quantity & Metrics
        MarketplaceListingRepository.increment_metric(listing, 'purchase_count')
        listing.quantity_available -= quantity
        listing.save()
        
        ListingService.sync_inventory_state(str(listing.id))
        
        listing_sold.send(sender=MarketplaceOrderService, listing=listing, order=mp_order)
        return mp_order


class RecommendationService:
    @staticmethod
    def get_ai_recommendations(customer_id: str, limit: int = 10) -> List[MarketplaceListing]:
        """
        Implementation ready for AI models. 
        Currently falls back to popularity heuristic.
        """
        return list(MarketplaceListing.objects.filter(
            listing_status=ListingStatus.PUBLISHED,
            is_deleted=False
        ).order_by('-purchase_count', '-views', '-created_at')[:limit])
