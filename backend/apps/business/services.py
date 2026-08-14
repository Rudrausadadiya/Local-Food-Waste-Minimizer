from django.db import transaction
from django.utils import timezone
from .models import Business, Address, Branch
from .repositories import BusinessRepository, AddressRepository, BranchRepository, OperatingHoursRepository
from django.utils.text import slugify
import uuid

# Class: BusinessRegistrationService
class BusinessRegistrationService:
    @staticmethod
    @transaction.atomic
    # Method: register_business
    def register_business(user, data: dict) -> Business:
        slug = slugify(data.get('business_name', ''))
        if Business.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        data['slug'] = slug
        data['owner'] = user
        data.setdefault('business_status', Business.BusinessStatus.APPROVED)
        data.setdefault('is_active', True)
        business = BusinessRepository.create(data)

        if not Branch.objects.filter(business=business).exists():
            Branch.objects.create(
                business=business,
                branch_name=f"{business.business_name} Main Branch",
                branch_code=f"BR-{uuid.uuid4().hex[:6].upper()}",
                is_main_branch=True,
                branch_status=Branch.BranchStatus.ACTIVE
            )
        return business

# Class: BusinessUpdateService
class BusinessUpdateService:
    @staticmethod
    @transaction.atomic
    # Method: update_business
    def update_business(business: Business, data: dict) -> Business:
        status = data.get('business_status')
        if status == Business.BusinessStatus.SUSPENDED:
            data['is_active'] = False
        elif status == Business.BusinessStatus.APPROVED:
            data['is_active'] = True
            data['is_verified'] = data.get('is_verified', True)
        elif status == Business.BusinessStatus.REJECTED:
            data['is_active'] = False

        updated = BusinessRepository.update(business, data)

        owner = updated.owner
        if owner:
            is_approved = updated.business_status == Business.BusinessStatus.APPROVED
            if is_approved and updated.is_verified:
                owner.is_active = True
                owner.save(update_fields=['is_active'])
                
                if getattr(owner, 'role', '') == 'NGO' or updated.business_type == 'NGO':
                    from apps.donations.models import NGO, NGOVerificationStatus
                    ngo = NGO.objects.filter(user=owner).first()
                    if ngo:
                        ngo.verification_status = NGOVerificationStatus.VERIFIED
                        ngo.is_active = True
                        ngo.save(update_fields=['verification_status', 'is_active'])
            elif updated.business_status in [Business.BusinessStatus.SUSPENDED, Business.BusinessStatus.REJECTED] or not updated.is_verified:
                owner.is_active = False
                owner.save(update_fields=['is_active'])
                if getattr(owner, 'role', '') == 'NGO' or updated.business_type == 'NGO':
                    from apps.donations.models import NGO, NGOVerificationStatus
                    ngo = NGO.objects.filter(user=owner).first()
                    if ngo:
                        ngo.verification_status = NGOVerificationStatus.REJECTED if updated.business_status == Business.BusinessStatus.REJECTED else NGOVerificationStatus.PENDING
                        ngo.is_active = False
                        ngo.save(update_fields=['verification_status', 'is_active'])

        # If verification was revoked or business status is no longer APPROVED:
        if not updated.is_verified or updated.business_status != Business.BusinessStatus.APPROVED:
            from apps.marketplace.models import MarketplaceListing, MarketplaceOrder, MarketplaceOrderStatus
            MarketplaceListing.objects.filter(business=updated).update(listing_status='UNPUBLISHED')

            # Cancel pending marketplace orders and notify customers
            pending_orders = MarketplaceOrder.objects.filter(
                listing__business=updated,
                status=MarketplaceOrderStatus.PENDING
            )
            from apps.notifications.models import Notification, NotificationCategory
            for order in pending_orders:
                order.status = MarketplaceOrderStatus.CANCELLED
                order.save(update_fields=['status'])

                target_user = order.user or (order.customer.user if order.customer else None)
                if target_user:
                    Notification.objects.create(
                        recipient=target_user,
                        title="Reservation Cancelled",
                        message=f"Your reservation for '{order.listing.listing_title}' at '{updated.business_name}' was cancelled because merchant verification was revoked. Any held points/funds have been released.",
                        category=NotificationCategory.ORDERS,
                    )

            # Cancel pending table/food reservations and notify customers
            from apps.reservations.models import Reservation
            pending_res = Reservation.objects.filter(business=updated, reservation_status__in=['PENDING', 'CONFIRMED'])
            for res in pending_res:
                res.reservation_status = 'CANCELLED'
                res.save(update_fields=['reservation_status'])

                if res.customer and res.customer.user:
                    Notification.objects.create(
                        recipient=res.customer.user,
                        title="Reservation Cancelled",
                        message=f"Your reservation at '{updated.business_name}' was cancelled as merchant verification status changed.",
                        category=NotificationCategory.RESERVATIONS,
                    )

        return updated

# Class: BusinessVerificationService
class BusinessVerificationService:
    @staticmethod
    # Method: verify_business
    def verify_business(business: Business) -> Business:
        return BusinessUpdateService.update_business(business, {'is_verified': True, 'business_status': Business.BusinessStatus.APPROVED})

# Class: BusinessDeactivationService
class BusinessDeactivationService:
    @staticmethod
    # Method: deactivate_business
    def deactivate_business(business: Business) -> Business:
        BusinessRepository.soft_delete(business)
        return business

# Class: BranchManagementService
class BranchManagementService:
    @staticmethod
    # Method: add_branch
    def add_branch(business: Business, data: dict) -> Branch:
        data['business'] = business
        return BranchRepository.create(data)

    @staticmethod
    # Method: update_branch
    def update_branch(branch: Branch, data: dict) -> Branch:
        return BranchRepository.update(branch, data)

# Class: AddressManagementService
class AddressManagementService:
    @staticmethod
    # Method: add_address
    def add_address(business: Business, data: dict) -> Address:
        data['business'] = business
        return AddressRepository.create(data)

    @staticmethod
    # Method: update_address
    def update_address(address: Address, data: dict) -> Address:
        return AddressRepository.update(address, data)

# Class: OperatingHoursService
class OperatingHoursService:
    @staticmethod
    # Method: set_operating_hours
    def set_operating_hours(business: Business, data: list) -> list:
        # data is a list of dicts with weekday, opening_time, closing_time, is_closed
        hours_list = []
        for item in data:
            defaults = {
                'opening_time': item.get('opening_time'),
                'closing_time': item.get('closing_time'),
                'is_closed': item.get('is_closed', False)
            }
            obj = OperatingHoursRepository.update_or_create(
                business_id=business.id,
                weekday=item['weekday'],
                defaults=defaults
            )
            hours_list.append(obj)
        return hours_list

# Class: BusinessSearchService
class BusinessSearchService:
    @staticmethod
    # Method: search_businesses
    def search_businesses(queryset, query_params: dict):
        # Filtering logic typically handled by django-filter in ViewSet,
        # but can be placed here if custom complex logic is needed.
        # Returning base queryset for viewset to filter on.
        return queryset

# Class: BusinessAnalyticsService
class BusinessAnalyticsService:
    @staticmethod
    # Method: get_business_stats
    def get_business_stats(business: Business) -> dict:
        return {
            'total_branches': business.branches.count(),
            'total_reviews': business.total_reviews,
            'average_rating': business.average_rating,
            'subscription_status': business.subscription_plan,
            'days_active': (timezone.now() - business.created_at).days if business.created_at else 0
        }
