from typing import Optional, Dict, Any
from .models import (
    NGO, NGODocument, DonationListing, DonationRequest, 
    DonationPickup, DonationHistory, DonationImpact, PickupRoute
)

# Class: NGORepository
class NGORepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(ngo_id: str) -> Optional[NGO]:
        return NGO.objects.filter(id=ngo_id).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> NGO:
        return NGO.objects.create(**data)

    @staticmethod
    # Method: update
    def update(ngo: NGO, data: Dict[str, Any]) -> NGO:
        for key, value in data.items():
            setattr(ngo, key, value)
        ngo.save()
        return ngo

# Class: NGODocumentRepository
class NGODocumentRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> NGODocument:
        return NGODocument.objects.create(**data)

# Class: DonationListingRepository
class DonationListingRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(listing_id: str) -> Optional[DonationListing]:
        return DonationListing.objects.filter(id=listing_id, is_deleted=False).first()

    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(listing_id: str) -> Optional[DonationListing]:
        return DonationListing.objects.select_for_update().filter(id=listing_id, is_deleted=False).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> DonationListing:
        return DonationListing.objects.create(**data)

    @staticmethod
    # Method: update
    def update(listing: DonationListing, data: Dict[str, Any]) -> DonationListing:
        for key, value in data.items():
            setattr(listing, key, value)
        listing.save()
        return listing

# Class: DonationRequestRepository
class DonationRequestRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(request_id: str) -> Optional[DonationRequest]:
        return DonationRequest.objects.filter(id=request_id).first()
        
    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(request_id: str) -> Optional[DonationRequest]:
        return DonationRequest.objects.select_for_update().filter(id=request_id).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> DonationRequest:
        return DonationRequest.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(req: DonationRequest, data: Dict[str, Any]) -> DonationRequest:
        for key, value in data.items():
            setattr(req, key, value)
        req.save()
        return req

# Class: DonationPickupRepository
class DonationPickupRepository:
    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(pickup_id: str) -> Optional[DonationPickup]:
        return DonationPickup.objects.select_for_update().filter(id=pickup_id).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> DonationPickup:
        return DonationPickup.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(pickup: DonationPickup, data: Dict[str, Any]) -> DonationPickup:
        for key, value in data.items():
            setattr(pickup, key, value)
        pickup.save()
        return pickup

# Class: DonationHistoryRepository
class DonationHistoryRepository:
    @staticmethod
    # Method: log_history
    def log_history(listing: DonationListing, previous_status: str, new_status: str, changed_by, remarks: str = "") -> DonationHistory:
        return DonationHistory.objects.create(
            donation_listing=listing,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks
        )

# Class: DonationImpactRepository
class DonationImpactRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> DonationImpact:
        return DonationImpact.objects.create(**data)
        
# Class: PickupRouteRepository
class PickupRouteRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> PickupRoute:
        return PickupRoute.objects.create(**data)
