from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.marketplace.models import ListingStatus
from apps.marketplace.services import MarketplaceOrderService

class MarketplaceServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test_place_order_insufficient_stock_fails(self):
        pass

    def test_listing_auto_deactivates_on_zero_stock(self):
        pass
