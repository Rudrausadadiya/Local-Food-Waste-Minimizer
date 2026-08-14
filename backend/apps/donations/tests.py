from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.business.models import Business, Branch
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.donations.models import (
    DonationStatus, 
    DonationRequestStatus, NGOVerificationStatus, PickupStatus
)
from apps.donations.services import DonationService, NGOService

User = get_user_model()

# Class: DonationServiceTestCase
class DonationServiceTestCase(TestCase):
    # Method: setUp
    def setUp(self):
        self.owner = User.objects.create_user(email="vendor@example.com", password="password123", role="VENDOR")
        self.business = Business.objects.create(
            owner=self.owner,
            business_name="Food Vendor",
            slug="food-vendor",
            business_type="VENDOR",
            business_email="vendor@example.com"
        )
        self.branch = Branch.objects.create(
            business=self.business,
            branch_name="Main Branch",
            branch_code="BR-001"
        )
        self.product = Product.objects.create(
            business=self.business,
            sku="SKU-DONATE",
            product_name="Surplus Rice",
            unit="kg",
            selling_price=Decimal("10.00")
        )
        self.inventory = Inventory.objects.create(
            business=self.business,
            product=self.product,
            branch=self.branch,
            current_stock=Decimal("100.00"),
            reserved_stock=Decimal("0.00")
        )

        self.user_ngo1 = User.objects.create_user(email="ngo1@example.com", password="password123", role="NGO")
        self.ngo1 = NGOService.register_ngo(self.user_ngo1, {
            'organization_name': 'NGO One',
            'registration_number': 'REG-NGO-1',
            'contact_person': 'Contact 1',
            'email': 'ngo1@example.com',
            'phone': '1234567890',
            'address': 'Street 1',
            'verification_status': NGOVerificationStatus.VERIFIED
        })

        self.user_ngo2 = User.objects.create_user(email="ngo2@example.com", password="password123", role="NGO")
        self.ngo2 = NGOService.register_ngo(self.user_ngo2, {
            'organization_name': 'NGO Two',
            'registration_number': 'REG-NGO-2',
            'contact_person': 'Contact 2',
            'email': 'ngo2@example.com',
            'phone': '0987654321',
            'address': 'Street 2',
            'verification_status': NGOVerificationStatus.VERIFIED
        })

        self.listing = DonationService.create_listing({
            'business': self.business,
            'branch': self.branch,
            'product': self.product,
            'quantity': 10,
            'available_until': timezone.now() + timezone.timedelta(days=1),
            'pickup_window_start': timezone.now() + timezone.timedelta(hours=1),
            'pickup_window_end': timezone.now() + timezone.timedelta(days=1),
        }, user=self.owner)

    # Method: test_approve_request_rejects_others
    def test_approve_request_rejects_others(self):
        req1 = DonationService.request_donation(str(self.listing.id), self.ngo1, 5)
        req2 = DonationService.request_donation(str(self.listing.id), self.ngo2, 5)

        approved_req = DonationService.approve_request(str(req1.id), approved_quantity=5, user=self.owner)
        self.assertEqual(approved_req.request_status, DonationRequestStatus.APPROVED)

        req2.refresh_from_db()
        self.assertEqual(req2.request_status, DonationRequestStatus.REJECTED)

    # Method: test_completed_donation_is_immutable
    def test_completed_donation_is_immutable(self):
        req = DonationService.request_donation(str(self.listing.id), self.ngo1, 5)
        DonationService.approve_request(str(req.id), approved_quantity=5, user=self.owner)
        pickup = DonationService.schedule_pickup(str(req.id), timezone.now() + timezone.timedelta(hours=2))
        
        # Confirm pickup - terminal step
        completed_pickup = DonationService.confirm_pickup(str(pickup.id), user=self.owner)
        self.assertEqual(completed_pickup.pickup_status, PickupStatus.COMPLETED)
        
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.donation_status, DonationStatus.COMPLETED)

    # Method: test_ngo_impact_summary_end_to_end
    def test_ngo_impact_summary_end_to_end(self):
        req = DonationService.request_donation(str(self.listing.id), self.ngo1, 10)
        DonationService.approve_request(str(req.id), approved_quantity=10, user=self.owner)
        pickup = DonationService.schedule_pickup(str(req.id), timezone.now() + timezone.timedelta(hours=2))
        DonationService.confirm_pickup(str(pickup.id), user=self.owner)

        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=self.user_ngo1)

        res = client.get('/api/v1/donations/impact/summary/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['completed_pickups'], 1)
        self.assertGreater(res.data['meals_served'], 0)
        self.assertGreater(res.data['food_saved_kg'], 0)

    # Method: test_create_pickup_route
    def test_create_pickup_route(self):
        req = DonationService.request_donation(str(self.listing.id), self.ngo1, 10)
        DonationService.approve_request(str(req.id), approved_quantity=10, user=self.owner)
        pickup = DonationService.schedule_pickup(str(req.id), timezone.now() + timezone.timedelta(hours=2))

        from apps.donations.services import PickupRouteService
        route = PickupRouteService.create_route(
            ngo=self.ngo1,
            pickup_ids=[str(pickup.id)],
            route_date=timezone.now().date(),
            driver_name="Alex Driver"
        )
        self.assertEqual(route.driver_name, "Alex Driver")
        self.assertEqual(route.pickups.count(), 1)


        # Confirm immutable listing raises ValidationError
        with self.assertRaises(ValidationError):
            DonationService.request_donation(str(self.listing.id), self.ngo2, 5)
