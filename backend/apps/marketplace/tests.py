from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.business.models import Business, Branch
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.orders.models import Customer
from apps.marketplace.models import ListingStatus
from apps.marketplace.services import ListingService, MarketplaceOrderService

User = get_user_model()

# Class: MarketplaceServiceTestCase
class MarketplaceServiceTestCase(TestCase):
    # Method: setUp
    def setUp(self):
        self.owner = User.objects.create_user(email="vendor_mkt@example.com", password="password123", role="VENDOR")
        self.business = Business.objects.create(
            owner=self.owner,
            business_name="Marketplace Vendor",
            slug="mkt-vendor",
            business_type="VENDOR",
            business_email="mkt_vendor@example.com"
        )
        self.branch = Branch.objects.create(
            business=self.business,
            branch_name="Main Branch",
            branch_code="BR-MKT-01"
        )
        self.product = Product.objects.create(
            business=self.business,
            sku="SKU-MKT",
            product_name="Surplus Cake",
            unit="pcs",
            selling_price=Decimal("20.00")
        )
        self.inventory = Inventory.objects.create(
            business=self.business,
            product=self.product,
            branch=self.branch,
            current_stock=Decimal("50.00")
        )
        self.customer = Customer.objects.create(
            business=self.business,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )

        self.listing = ListingService.create_listing({
            'business': self.business,
            'branch': self.branch,
            'product': self.product,
            'listing_title': 'Surplus Cake Sale',
            'original_price': Decimal('20.00'),
            'discounted_price': Decimal('10.00'),
            'quantity_available': 1,
            'expires_at': timezone.now() + timezone.timedelta(days=1),
        }, user=self.owner)
        ListingService.publish_listing(str(self.listing.id))

    # Method: test_place_order_insufficient_stock_fails
    def test_place_order_insufficient_stock_fails(self):
        with self.assertRaises(ValidationError):
            MarketplaceOrderService.place_order(
                listing_id=str(self.listing.id),
                customer=self.customer,
                quantity=5,
                user=self.owner
            )

    # Method: test_listing_auto_deactivates_on_zero_stock
    def test_listing_auto_deactivates_on_zero_stock(self):
        # Order the only 1 available unit
        order = MarketplaceOrderService.place_order(
            listing_id=str(self.listing.id),
            customer=self.customer,
            quantity=1,
            user=self.owner
        )
        self.assertIsNotNone(order)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.quantity_available, 0)
        self.assertIn(self.listing.listing_status, [ListingStatus.PAUSED, ListingStatus.EXPIRED])

    # Method: test_marketplace_review_restricted_to_purchasers
    def test_marketplace_review_restricted_to_purchasers(self):
        from rest_framework.test import APIClient
        client = APIClient()
        cust_user = User.objects.create_user(email="john@example.com", password="password123", role="CUSTOMER")
        client.force_authenticate(user=cust_user)

        # Attempting review before completed order must fail
        res = client.post('/api/v1/marketplace/reviews/', {
            'listing': str(self.listing.id),
            'rating': 5,
            'review': 'Great cake!'
        })
        self.assertEqual(res.status_code, 400)

        # Complete order first
        order = MarketplaceOrderService.place_order(
            listing_id=str(self.listing.id),
            customer=self.customer,
            quantity=1,
            user=self.owner
        )
        from apps.marketplace.models import MarketplaceOrderStatus
        order.status = MarketplaceOrderStatus.COMPLETED
        order.save()

        # Review after completed order succeeds
        res2 = client.post('/api/v1/marketplace/reviews/', {
            'listing': str(self.listing.id),
            'rating': 5,
            'review': 'Great cake!'
        })
        self.assertEqual(res2.status_code, 201)
        self.assertEqual(res2.data['rating'], 5)

    # Method: test_marketplace_review_unauthenticated_or_unlinked_user_fails
    def test_marketplace_review_unauthenticated_or_unlinked_user_fails(self):
        from rest_framework.test import APIClient
        from apps.orders.models import Customer
        client = APIClient()
        unlinked_user = User.objects.create_user(email="unlinked@example.com", password="password123", role="CUSTOMER")
        client.force_authenticate(user=unlinked_user)

        initial_customer_count = Customer.objects.count()

        # Attempt review for listing without any prior order
        res = client.post('/api/v1/marketplace/reviews/', {
            'listing': str(self.listing.id),
            'rating': 4,
            'review': 'Attempting fake review'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("You can only review listings you've completed an order for.", str(res.data))

        # Assert no junk Customer rows were created during the failed review attempt
        self.assertEqual(Customer.objects.count(), initial_customer_count)

