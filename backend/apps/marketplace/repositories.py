from typing import Optional, Dict, Any
from .models import MarketplaceListing, MarketplaceOrder, Wishlist, MarketplaceReview

# Class: MarketplaceListingRepository
class MarketplaceListingRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(listing_id: str) -> Optional[MarketplaceListing]:
        return MarketplaceListing.objects.filter(id=listing_id, is_deleted=False).first()

    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(listing_id: str) -> Optional[MarketplaceListing]:
        return MarketplaceListing.objects.select_for_update().filter(id=listing_id, is_deleted=False).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> MarketplaceListing:
        return MarketplaceListing.objects.create(**data)

    @staticmethod
    # Method: update
    def update(listing: MarketplaceListing, data: Dict[str, Any]) -> MarketplaceListing:
        for key, value in data.items():
            setattr(listing, key, value)
        listing.save()
        return listing

    @staticmethod
    # Method: soft_delete
    def soft_delete(listing: MarketplaceListing) -> None:
        listing.is_deleted = True
        listing.save(update_fields=['is_deleted', 'updated_at'])

    @staticmethod
    # Method: increment_metric
    def increment_metric(listing: MarketplaceListing, metric_field: str) -> None:
        # Avoid select_for_update overhead for simple metric increments
        from django.db.models import F
        MarketplaceListing.objects.filter(id=listing.id).update(**{metric_field: F(metric_field) + 1})


# Class: MarketplaceOrderRepository
class MarketplaceOrderRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(order_id: str) -> Optional[MarketplaceOrder]:
        return MarketplaceOrder.objects.filter(id=order_id).first()

    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(order_id: str) -> Optional[MarketplaceOrder]:
        return MarketplaceOrder.objects.select_for_update().filter(id=order_id).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> MarketplaceOrder:
        return MarketplaceOrder.objects.create(**data)

    @staticmethod
    # Method: update
    def update(order: MarketplaceOrder, data: Dict[str, Any]) -> MarketplaceOrder:
        for key, value in data.items():
            setattr(order, key, value)
        order.save()
        return order


# Class: WishlistRepository
class WishlistRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Wishlist:
        return Wishlist.objects.create(**data)
        
    @staticmethod
    # Method: delete
    def delete(customer_id: str, listing_id: str) -> bool:
        deleted, _ = Wishlist.objects.filter(customer_id=customer_id, listing_id=listing_id).delete()
        return deleted > 0


# Class: MarketplaceReviewRepository
class MarketplaceReviewRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> MarketplaceReview:
        return MarketplaceReview.objects.create(**data)
