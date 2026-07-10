from django.db import transaction
from django.utils import timezone
from .models import Business, Address, Branch, OperatingHours
from .repositories import BusinessRepository, AddressRepository, BranchRepository, OperatingHoursRepository
from django.utils.text import slugify
import uuid

class BusinessRegistrationService:
    @staticmethod
    @transaction.atomic
    def register_business(user, data: dict) -> Business:
        slug = slugify(data.get('business_name', ''))
        if Business.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        data['slug'] = slug
        data['owner'] = user
        return BusinessRepository.create(data)

class BusinessUpdateService:
    @staticmethod
    def update_business(business: Business, data: dict) -> Business:
        return BusinessRepository.update(business, data)

class BusinessVerificationService:
    @staticmethod
    def verify_business(business: Business) -> Business:
        return BusinessRepository.update(business, {'is_verified': True, 'business_status': Business.BusinessStatus.APPROVED})

class BusinessDeactivationService:
    @staticmethod
    def deactivate_business(business: Business) -> Business:
        BusinessRepository.soft_delete(business)
        return business

class BranchManagementService:
    @staticmethod
    def add_branch(business: Business, data: dict) -> Branch:
        data['business'] = business
        return BranchRepository.create(data)

    @staticmethod
    def update_branch(branch: Branch, data: dict) -> Branch:
        return BranchRepository.update(branch, data)

class AddressManagementService:
    @staticmethod
    def add_address(business: Business, data: dict) -> Address:
        data['business'] = business
        return AddressRepository.create(data)

    @staticmethod
    def update_address(address: Address, data: dict) -> Address:
        return AddressRepository.update(address, data)

class OperatingHoursService:
    @staticmethod
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

class BusinessSearchService:
    @staticmethod
    def search_businesses(queryset, query_params: dict):
        # Filtering logic typically handled by django-filter in ViewSet,
        # but can be placed here if custom complex logic is needed.
        # Returning base queryset for viewset to filter on.
        return queryset

class BusinessAnalyticsService:
    @staticmethod
    def get_business_stats(business: Business) -> dict:
        return {
            'total_branches': business.branches.count(),
            'total_reviews': business.total_reviews,
            'average_rating': business.average_rating,
            'subscription_status': business.subscription_plan,
            'days_active': (timezone.now() - business.created_at).days if business.created_at else 0
        }
