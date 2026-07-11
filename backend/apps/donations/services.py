import math
from typing import Dict, Any, List
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    NGOVerificationStatus, DonationStatus, DonationRequestStatus,
    PickupStatus, DonationListing, DonationRequest, DonationPickup, NGO
)
from .repositories import (
    NGORepository, DonationListingRepository, DonationRequestRepository,
    DonationPickupRepository, DonationHistoryRepository, DonationImpactRepository
)
from .validators import (
    validate_ngo_verified, validate_inventory_for_donation,
    validate_donation_immutable, validate_inventory_batch_for_donation
)
from .signals import (
    ngo_registered, ngo_verified, donation_listed, donation_requested,
    donation_approved, pickup_scheduled, donation_completed, donation_expired,
    donation_expiring, pickup_reminder, pickup_delayed, impact_calculated
)
from apps.inventory.services import InventoryService
from apps.inventory.models import Inventory

class NGOService:
    @staticmethod
    @transaction.atomic
    def register_ngo(user, data: Dict[str, Any]) -> NGO:
        data['user'] = user
        ngo = NGORepository.create(data)
        ngo_registered.send(sender=NGOService, ngo=ngo)
        return ngo

    @staticmethod
    @transaction.atomic
    def verify_ngo(ngo_id: str, admin_user) -> NGO:
        ngo = NGORepository.get_by_id(ngo_id)
        if not ngo:
            raise ValidationError("NGO not found.")
        ngo = NGORepository.update(ngo, {'verification_status': NGOVerificationStatus.VERIFIED})
        ngo_verified.send(sender=NGOService, ngo=ngo, verifier=admin_user)
        return ngo


class DonationService:
    @staticmethod
    @transaction.atomic
    def create_listing(data: Dict[str, Any], user=None) -> DonationListing:
        validate_inventory_for_donation(data['product'], str(data['branch'].id), data['quantity'])
        if 'inventory_batch' in data and data['inventory_batch']:
            validate_inventory_batch_for_donation(data['inventory_batch'])
            
        data['created_by'] = user
        listing = DonationListingRepository.create(data)
        
        DonationHistoryRepository.log_history(
            listing, None, DonationStatus.ACTIVE, user, "Listing created."
        )
        donation_listed.send(sender=DonationService, listing=listing)
        return listing

    @staticmethod
    @transaction.atomic
    def convert_from_marketplace(marketplace_listing_id: str, user=None) -> DonationListing:
        from apps.marketplace.models import MarketplaceListing, ListingStatus
        from apps.marketplace.repositories import MarketplaceListingRepository
        from apps.marketplace.services import ListingService
        
        ml = MarketplaceListingRepository.get_by_id_for_update(marketplace_listing_id)
        if not ml or ml.listing_status != ListingStatus.PUBLISHED:
            raise ValidationError("Marketplace listing is not eligible for conversion.")
            
        # Create donation listing with remaining qty
        listing = DonationService.create_listing({
            'business': ml.business,
            'branch': ml.branch,
            'product': ml.product,
            'inventory_batch': ml.inventory_batch,
            'quantity': ml.quantity_available,
            'available_until': timezone.now() + timezone.timedelta(days=1),
            'pickup_window_start': timezone.now() + timezone.timedelta(hours=1),
            'pickup_window_end': timezone.now() + timezone.timedelta(days=1),
        }, user)
        
        # Close marketplace listing
        ListingService.close_listing(str(ml.id))
        
        return listing

    @staticmethod
    @transaction.atomic
    def request_donation(listing_id: str, ngo: NGO, requested_quantity: int) -> DonationRequest:
        validate_ngo_verified(ngo)
        listing = DonationListingRepository.get_by_id_for_update(listing_id)
        if not listing or listing.donation_status != DonationStatus.ACTIVE:
            raise ValidationError("Donation is not available.")
            
        if requested_quantity > listing.quantity:
            raise ValidationError("Requested quantity exceeds available listing quantity.")
            
        req = DonationRequestRepository.create({
            'donation_listing': listing,
            'ngo': ngo,
            'requested_quantity': requested_quantity
        })
        
        listing.donation_status = DonationStatus.REQUESTED
        listing.save()
        
        donation_requested.send(sender=DonationService, request=req)
        return req

    @staticmethod
    @transaction.atomic
    def approve_request(request_id: str, approved_quantity: int, user=None) -> DonationRequest:
        req = DonationRequestRepository.get_by_id_for_update(request_id)
        if not req or req.request_status != DonationRequestStatus.PENDING:
            raise ValidationError("Invalid request state for approval.")
            
        listing = DonationListingRepository.get_by_id_for_update(str(req.donation_listing.id))
        validate_donation_immutable(listing)
        
        if listing.donation_status == DonationStatus.RESERVED:
            raise ValidationError("Another request has already been approved for this listing. Only one approved NGO per donation allowed.")
            
        if approved_quantity > listing.quantity:
            raise ValidationError("Approved quantity exceeds available listing quantity.")

        # Reject all other requests for this listing
        DonationRequest.objects.filter(donation_listing=listing).exclude(id=req.id).update(request_status=DonationRequestStatus.REJECTED)
        
        req.approved_quantity = approved_quantity
        req.request_status = DonationRequestStatus.APPROVED if approved_quantity == req.requested_quantity else DonationRequestStatus.PARTIALLY_APPROVED
        req.save()
        
        listing.donation_status = DonationStatus.RESERVED
        listing.save()
        
        # Reserve stock via InventoryService
        inventory = Inventory.objects.filter(product_id=listing.product.id, branch_id=listing.branch.id).first()
        if inventory:
            InventoryService.reserve_stock(str(inventory.id), Decimal(str(approved_quantity)))
        
        DonationHistoryRepository.log_history(
            listing, DonationStatus.REQUESTED, DonationStatus.RESERVED, user, f"Approved request for {req.ngo.organization_name}"
        )
        
        donation_approved.send(sender=DonationService, request=req)
        return req

    @staticmethod
    @transaction.atomic
    def schedule_pickup(request_id: str, pickup_time) -> DonationPickup:
        req = DonationRequestRepository.get_by_id_for_update(request_id)
        if not req or req.request_status not in [DonationRequestStatus.APPROVED, DonationRequestStatus.PARTIALLY_APPROVED]:
            raise ValidationError("Request must be approved to schedule pickup.")
            
        pickup = DonationPickupRepository.create({
            'donation_request': req,
            'pickup_time': pickup_time,
            'collected_by': req.ngo.contact_person
        })
        
        pickup_scheduled.send(sender=DonationService, pickup=pickup)
        return pickup

    @staticmethod
    @transaction.atomic
    def confirm_pickup(pickup_id: str, user=None) -> DonationPickup:
        pickup = DonationPickupRepository.get_by_id_for_update(pickup_id)
        if not pickup or pickup.pickup_status == PickupStatus.COMPLETED:
            raise ValidationError("Invalid pickup state.")
            
        listing = pickup.donation_request.donation_listing
        validate_donation_immutable(listing)

        # Release reserved stock and deduct it (Stock out) via InventoryService
        inventory = Inventory.objects.filter(product_id=listing.product.id, branch_id=listing.branch.id).first()
        if inventory:
            InventoryService.release_stock(str(inventory.id), Decimal(str(pickup.donation_request.approved_quantity)))
            InventoryService.deduct_stock(str(inventory.id), Decimal(str(pickup.donation_request.approved_quantity)), reason="DONATION")

        pickup.pickup_status = PickupStatus.COMPLETED
        pickup.save()
        
        listing.donation_status = DonationStatus.COMPLETED
        listing.save()
        
        DonationHistoryRepository.log_history(
            listing, DonationStatus.RESERVED, DonationStatus.COMPLETED, user, "Pickup completed."
        )
        
        # Calculate Impact
        food_weight = Decimal(str(pickup.donation_request.approved_quantity)) * Decimal('0.5') # Arbitrary default multiplier
        impact = DonationImpactRepository.create({
            'donation_pickup': pickup,
            'meals_served': pickup.donation_request.approved_quantity * 2,
            'food_saved_kg': food_weight,
            'carbon_saved_kg': food_weight * Decimal('2.5'), # Example conversion rate
            'beneficiaries': pickup.donation_request.approved_quantity
        })
        
        donation_completed.send(sender=DonationService, pickup=pickup)
        impact_calculated.send(sender=DonationService, impact=impact)
        return pickup


class MatchingService:
    @staticmethod
    def get_nearby_ngos(latitude: float, longitude: float, max_distance_km: float = 50.0) -> List[NGO]:
        """
        Placeholder for AI-based Matching. Currently uses simple Haversine formula logic.
        """
        ngos = NGO.objects.filter(
            verification_status=NGOVerificationStatus.VERIFIED,
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        matched_ngos = []
        for ngo in ngos:
            # Haversine distance
            R = 6371.0 # Earth radius in km
            lat1 = math.radians(latitude)
            lon1 = math.radians(longitude)
            lat2 = math.radians(float(ngo.latitude))
            lon2 = math.radians(float(ngo.longitude))
            
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            
            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            
            if distance <= max_distance_km and distance <= float(ngo.service_radius):
                ngo.calculated_distance = distance
                matched_ngos.append(ngo)
                
        return sorted(matched_ngos, key=lambda x: x.calculated_distance)
