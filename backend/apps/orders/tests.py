from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.business.models import Business, Branch
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.orders.models import OrderStatus, PaymentStatus, PaymentGateway, OrderType, Customer
from apps.orders.services import OrderService

User = get_user_model()

# Class: OrderServiceTestCase
class OrderServiceTestCase(TestCase):
    # Method: setUp
    def setUp(self):
        self.owner = User.objects.create_user(email="order_owner@example.com", password="password123", role="VENDOR")
        self.business = Business.objects.create(
            owner=self.owner,
            business_name="Order Business",
            slug="order-business",
            business_type="VENDOR",
            business_email="order_owner@example.com"
        )
        self.branch = Branch.objects.create(
            business=self.business,
            branch_name="Main Branch",
            branch_code="BR-ORD-01"
        )
        self.product = Product.objects.create(
            business=self.business,
            sku="SKU-ORD",
            product_name="Pizza",
            unit="box",
            selling_price=Decimal("15.00")
        )
        self.inventory = Inventory.objects.create(
            business=self.business,
            product=self.product,
            branch=self.branch,
            current_stock=Decimal("1000.00")
        )
        self.customer = Customer.objects.create(
            business=self.business,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )

    # Method: test_cancel_completed_order_fails
    def test_cancel_completed_order_fails(self):
        order = OrderService.create_order({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'order_number': 'ORD-1001',
            'order_type': OrderType.DINE_IN,
            'payment_status': PaymentStatus.COMPLETED
        }, [{'product': self.product, 'quantity': 1, 'unit_price': Decimal('15.00')}])

        OrderService.complete_order(str(order.id))
        order.refresh_from_db()
        self.assertEqual(order.order_status, OrderStatus.COMPLETED)

        with self.assertRaises(ValidationError):
            OrderService.cancel_order(str(order.id))

    # Method: test_complete_unpaid_order_fails
    def test_complete_unpaid_order_fails(self):
        order = OrderService.create_order({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'order_number': 'ORD-1002',
            'order_type': OrderType.ONLINE,
            'payment_method': PaymentGateway.STRIPE,
            'payment_status': PaymentStatus.PENDING
        }, [{'product': self.product, 'quantity': 1, 'unit_price': Decimal('15.00')}])

        with self.assertRaises(ValidationError):
            OrderService.complete_order(str(order.id))

    # Method: test_delete_paid_order_fails
    def test_delete_paid_order_fails(self):
        order = OrderService.create_order({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'order_number': 'ORD-1003',
            'order_type': OrderType.DINE_IN,
            'payment_status': PaymentStatus.COMPLETED
        }, [{'product': self.product, 'quantity': 1, 'unit_price': Decimal('15.00')}])

        with self.assertRaises(ValidationError):
            OrderService.delete_order(str(order.id))

    # Method: test_loyalty_points_earned_and_redeemed
    def test_loyalty_points_earned_and_redeemed(self):
        # Create order for ₹500
        order = OrderService.create_order({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'order_number': 'ORD-LOYALTY-1',
            'order_type': OrderType.DINE_IN,
            'payment_status': PaymentStatus.COMPLETED
        }, [{'product': self.product, 'quantity': 50, 'unit_price': Decimal('10.00')}])

        # Complete order to earn 5 points (500 // 100)
        OrderService.complete_order(str(order.id))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.loyalty_points, 5)

        # Redeem 3 points on new order
        order2 = OrderService.create_order({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'order_number': 'ORD-LOYALTY-2',
            'order_type': OrderType.DINE_IN,
            'redeem_points': 3
        }, [{'product': self.product, 'quantity': 1, 'unit_price': Decimal('15.00')}])

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.loyalty_points, 2)
        self.assertEqual(order2.discount_amount, Decimal('3.00'))

    # Method: test_delivery_status_transitions
    def test_delivery_status_transitions(self):
        from apps.orders.services import DeliveryService
        order = OrderService.create_order({
            'business': self.business,
            'branch': self.branch,
            'customer': self.customer,
            'order_number': 'ORD-DELIVERY-1',
            'order_type': OrderType.DELIVERY,
            'delivery_address': '123 Test St'
        }, [{'product': self.product, 'quantity': 1, 'unit_price': Decimal('15.00')}])

        self.assertTrue(hasattr(order, 'delivery'))
        delivery = order.delivery
        self.assertEqual(delivery.status, 'PENDING')

        # Direct jump to DELIVERED without DISPATCHED must raise ValidationError
        with self.assertRaises(ValidationError):
            DeliveryService.mark_delivered(str(delivery.id))

        # Valid transition PENDING -> DISPATCHED -> DELIVERED
        DeliveryService.dispatch_delivery(str(delivery.id))
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'DISPATCHED')

        DeliveryService.mark_delivered(str(delivery.id))
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'DELIVERED')

