from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from django.utils import timezone
from .models import (
    NGO, NGODocument, DonationListing, DonationRequest, 
    DonationPickup, DonationHistory, DonationImpact, PickupRoute
)

class NGORepository:
    @staticmethod
    def get_by_id(ngo_id: str) -> Optional[NGO]:
        return NGO.objects.filter(id=ngo_id).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> NGO:
        return NGO.objects.create(**data)

    @staticmethod
    def update(ngo: NGO, data: Dict[str, Any]) -> NGO:
        for key, value in data.items():
            setattr(ngo, key, value)
        ngo.save()
        return ngo

class NGODocumentRepository:
    @staticmethod
    def create(data: Dict[str, Any]) -> NGODocument:
        return NGODocument.objects.create(**data)

class DonationListingRepository:
    @staticmethod
    def get_by_id(listing_id: str) -> Optional[DonationListing]:
        return DonationListing.objects.filter(id=listing_id, is_deleted=False).first()

    @staticmethod
    def get_by_id_for_update(listing_id: str) -> Optional[DonationListing]:
        return DonationListing.objects.select_for_update().filter(id=listing_id, is_deleted=False).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> DonationListing:
        return DonationListing.objects.create(**data)

    @staticmethod
    def update(listing: DonationListing, data: Dict[str, Any]) -> DonationListing:
        for key, value in data.items():
            setattr(listing, key, value)
        listing.save()
        return listing

class DonationRequestRepository:
    @staticmethod
    def get_by_id(request_id: str) -> Optional[DonationRequest]:
        return DonationRequest.objects.filter(id=request_id).first()
        
    @staticmethod
    def get_by_id_for_update(request_id: str) -> Optional[DonationRequest]:
        return DonationRequest.objects.select_for_update().filter(id=request_id).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> DonationRequest:
        return DonationRequest.objects.create(**data)
        
    @staticmethod
    def update(req: DonationRequest, data: Dict[str, Any]) -> DonationRequest:
        for key, value in data.items():
            setattr(req, key, value)
        req.save()
        return req

class DonationPickupRepository:
    @staticmethod
    def get_by_id_for_update(pickup_id: str) -> Optional[DonationPickup]:
        return DonationPickup.objects.select_for_update().filter(id=pickup_id).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> DonationPickup:
        return DonationPickup.objects.create(**data)
        
    @staticmethod
    def update(pickup: DonationPickup, data: Dict[str, Any]) -> DonationPickup:
        for key, value in data.items():
            setattr(pickup, key, value)
        pickup.save()
        return pickup

class DonationHistoryRepository:
    @staticmethod
    def log_history(listing: DonationListing, previous_status: str, new_status: str, changed_by, remarks: str = "") -> DonationHistory:
        return DonationHistory.objects.create(
            donation_listing=listing,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks
        )

class DonationImpactRepository:
    @staticmethod
    def create(data: Dict[str, Any]) -> DonationImpact:
        return DonationImpact.objects.create(**data)
        
class PickupRouteRepository:
    @staticmethod
    def create(data: Dict[str, Any]) -> PickupRoute:
        return PickupRoute.objects.create(**data)
