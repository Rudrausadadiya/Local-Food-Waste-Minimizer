from datetime import time, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.business.models import Business, Branch
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.orders.models import Customer
from apps.reservations.models import ReservationStatus
from apps.reservations.services import ReservationService

User = get_user_model()

# Class: ReservationServiceTestCase
class ReservationServiceTestCase(TestCase):
    # Method: setUp
    def setUp(self):
        self.owner = User.objects.create_user(email="res_owner@example.com", password="password123", role="VENDOR")
        self.business = Business.objects.create(
            owner=self.owner,
            business_name="Reservation Business",
            slug="res-business",
            business_type="VENDOR",
            business_email="res_owner@example.com"
        )
        self.branch = Branch.objects.create(
            business=self.business,
            branch_name="Main Branch",
            branch_code="BR-RES-01"
        )
        self.product = Product.objects.create(
            business=self.business,
            sku="SKU-RES",
            product_name="Dinner Combo",
            unit="set",
            selling_price=Decimal("25.00")
        )
        self.inventory = Inventory.objects.create(
            business=self.business,
            product=self.product,
            branch=self.branch,
            current_stock=Decimal("100.00")
        )
        self.customer = Customer.objects.create(
            business=self.business,
            first_name="Alice",
            last_name="Wong",
            email="alice@example.com"
        )

        self.reservation = ReservationService.create_reservation({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'reservation_number': 'RES-2001',
            'reservation_date': timezone.now().date() + timedelta(days=1),
            'reservation_time': time(19, 0),
            'expected_duration': timedelta(hours=2),
            'party_size': 2,
        }, items_data=[{'product': self.product, 'quantity': 2, 'reserved_price': Decimal('25.00')}], user=self.owner)

    # Method: test_modify_completed_reservation_fails
    def test_modify_completed_reservation_fails(self):
        ReservationService.confirm_reservation(str(self.reservation.id), user=self.owner)
        ReservationService.convert_to_order(str(self.reservation.id), user=self.owner)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.reservation_status, ReservationStatus.COMPLETED)

        with self.assertRaises(ValidationError):
            ReservationService.modify_reservation(str(self.reservation.id), {'party_size': 4}, user=self.owner)

    # Method: test_convert_unconfirmed_reservation_fails
    def test_convert_unconfirmed_reservation_fails(self):
        ReservationService.cancel_reservation(str(self.reservation.id), user=self.owner)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.reservation_status, ReservationStatus.CANCELLED)

        with self.assertRaises(ValidationError):
            ReservationService.convert_to_order(str(self.reservation.id), user=self.owner)
