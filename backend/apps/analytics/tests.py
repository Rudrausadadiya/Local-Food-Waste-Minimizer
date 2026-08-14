from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.users.models import User
from apps.business.models import Business, Branch
from apps.products.models import Product, Category
from apps.inventory.models import Inventory
from apps.orders.models import Order, Customer
from apps.reservations.models import Reservation, ReservationStatus, ReservationType
from .services import DataQualityService, DatasetService, ReportService

# Class: AnalyticsServiceTests
class AnalyticsServiceTests(TestCase):
    # Method: setUp
    def setUp(self):
        self.user = User.objects.create_user(email="analytics_owner@example.com", password="Password123!")
        self.business = Business.objects.create(
            owner=self.user,
            business_name="Analytics Test Business",
            slug="analytics-test-biz",
            business_type="VENDOR",
            business_email="analytics@biz.com",
            business_phone="1234567890"
        )
        self.branch = Branch.objects.create(
            business=self.business,
            branch_name="Main Branch",
            branch_code="MAIN01",
            phone="1234567890",
            email="main@biz.com"
        )
        self.category = Category.objects.create(business=self.business, name="Food")
        self.product = Product.objects.create(
            business=self.business,
            category=self.category,
            product_name="Test Product",
            unit="kg",
            sku="SKU-001",
            cost_price=Decimal("5.00"),
            selling_price=Decimal("10.00")
        )
        self.customer = Customer.objects.create(
            business=self.business,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com"
        )

    # Method: test_detect_anomalies_real_queries
    def test_detect_anomalies_real_queries(self):
        # 1. Seed negative stock (bypassing normal service/clean validation via update)
        inv = Inventory.objects.create(
            business=self.business,
            branch=self.branch,
            product=self.product,
            current_stock=Decimal("10.00")
        )
        Inventory.objects.filter(pk=inv.pk).update(current_stock=Decimal("-10.00"))

        # 2. Seed orphaned order (Order with 0 items)
        Order.objects.create(
            business=self.business,
            branch=self.branch,
            customer=self.customer,
            order_number="ORD-ORPHAN-01",
            total_amount=Decimal("0.00")
        )

        # 3. Seed unlinked TABLE reservation (Reservation with 0 reserved_tables)
        Reservation.objects.create(
            business=self.business,
            branch=self.branch,
            customer=self.customer,
            reservation_number="RES-UNLINKED-01",
            reservation_type=ReservationType.TABLE,
            reservation_status=ReservationStatus.CONFIRMED,
            reservation_date=timezone.now().date(),
            reservation_time=timezone.now().time(),
            expected_duration=timezone.timedelta(hours=1)
        )

        anomalies = DataQualityService.detect_anomalies(business_id=str(self.business.id))

        self.assertEqual(anomalies['negative_inventory'], 1)
        self.assertEqual(anomalies['orphaned_orders'], 1)
        self.assertEqual(anomalies['unlinked_reservations'], 1)

    # Method: test_extract_training_dataset_csv
    def test_extract_training_dataset_csv(self):
        Order.objects.create(
            business=self.business,
            branch=self.branch,
            customer=self.customer,
            order_number="ORD-DS-01",
            total_amount=Decimal("150.00")
        )

        csv_content = DatasetService.extract_training_dataset('FORECAST', business_id=str(self.business.id))
        
        self.assertIn('date,sales_volume', csv_content)
        self.assertIn('150.0', csv_content)

    # Method: test_generate_report_sales_and_inventory
    def test_generate_report_sales_and_inventory(self):
        Order.objects.create(
            business=self.business,
            branch=self.branch,
            customer=self.customer,
            order_number="ORD-REP-01",
            total_amount=Decimal("85.50")
        )
        Inventory.objects.create(
            business=self.business,
            branch=self.branch,
            product=self.product,
            current_stock=Decimal("42.00")
        )

        start_date = timezone.now() - timezone.timedelta(days=1)
        end_date = timezone.now() + timezone.timedelta(days=1)

        sales_csv = ReportService.generate_report('SALES', start_date, end_date, 'CSV', business_id=str(self.business.id))
        self.assertIn('ORD-REP-01', sales_csv)
        self.assertIn('85.5', sales_csv)

        inv_json = ReportService.generate_report('INVENTORY', start_date, end_date, 'JSON', business_id=str(self.business.id))
        self.assertIn('Test Product', inv_json)
        self.assertIn('42.0', inv_json)
