from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.business.models import Business, Branch
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.inventory.services import InventoryService

User = get_user_model()

# Class: InventoryServiceTestCase
class InventoryServiceTestCase(TestCase):
    # Method: setUp
    def setUp(self):
        self.user = User.objects.create_user(email="inventory_user@example.com", password="password123", role="VENDOR")
        self.business = Business.objects.create(
            owner=self.user,
            business_name="Inventory Business",
            slug="inventory-business",
            business_type="VENDOR",
            business_email="inventory_user@example.com"
        )
        self.branch = Branch.objects.create(
            business=self.business,
            branch_name="Main Branch",
            branch_code="BR-INV-01"
        )
        self.product = Product.objects.create(
            business=self.business,
            sku="SKU-INV",
            product_name="Flour",
            unit="kg",
            selling_price=Decimal("2.50")
        )
        self.inventory = Inventory.objects.create(
            business=self.business,
            product=self.product,
            branch=self.branch,
            current_stock=Decimal("0.00")
        )

    # Method: test_stock_in_and_stock_out
    def test_stock_in_and_stock_out(self):
        batch_details = {
            'batch_number': 'BATCH-001',
            'expiry_date': timezone.now().date() + timezone.timedelta(days=30)
        }
        
        # Stock In 50 kg
        InventoryService.stock_in(
            inventory_id=str(self.inventory.id),
            quantity=Decimal("50.00"),
            user_id=str(self.user.id),
            batch_details=batch_details,
            remarks="Initial Stock In"
        )
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.current_stock, Decimal("50.00"))

        # Stock Out 20 kg
        InventoryService.stock_out(
            inventory_id=str(self.inventory.id),
            quantity=Decimal("20.00"),
            user_id=str(self.user.id),
            remarks="Usage Stock Out"
        )
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.current_stock, Decimal("30.00"))
