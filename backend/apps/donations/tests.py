from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.donations.models import DonationStatus
from apps.donations.services import DonationService

class DonationServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test_approve_request_rejects_others(self):
        pass

    def test_completed_donation_is_immutable(self):
        pass
