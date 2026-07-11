from django.test import TestCase
from decimal import Decimal
from apps.reservations.models import ReservationStatus
from apps.reservations.services import ReservationService
from django.core.exceptions import ValidationError

class ReservationServiceTestCase(TestCase):
    def setUp(self):
        # Setting up factories would be required here.
        pass

    def test_modify_completed_reservation_fails(self):
        pass

    def test_convert_unconfirmed_reservation_fails(self):
        pass
