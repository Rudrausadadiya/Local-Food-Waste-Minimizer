import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Class: PaymentGateway
class PaymentGateway(models.TextChoices):
    CASH = 'CASH', _('Cash')
    STRIPE = 'STRIPE', _('Stripe')
    PAYPAL = 'PAYPAL', _('PayPal')
    RAZORPAY = 'RAZORPAY', _('Razorpay')
    OTHER = 'OTHER', _('Other')

# Class: PaymentStatus
class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    COMPLETED = 'COMPLETED', _('Completed')
    FAILED = 'FAILED', _('Failed')
    REFUNDED = 'REFUNDED', _('Refunded')

# Class: OrderStatus
class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    PROCESSING = 'PROCESSING', _('Processing')
    READY = 'READY', _('Ready')
    COMPLETED = 'COMPLETED', _('Completed')
    CANCELLED = 'CANCELLED', _('Cancelled')
    REFUNDED = 'REFUNDED', _('Refunded')

# Class: OrderType
class OrderType(models.TextChoices):
    DINE_IN = 'DINE_IN', _('Dine In')
    TAKEAWAY = 'TAKEAWAY', _('Takeaway')
    DELIVERY = 'DELIVERY', _('Delivery')
    ONLINE = 'ONLINE', _('Online')

# Class: Customer
class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profiles')
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        ordering = ['-created_at']
        unique_together = ('business', 'phone', 'email')

    # Method: __str__
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


# Class: Order
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='orders')
    branch = models.ForeignKey('business.Branch', on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    reservation_id = models.UUIDField(null=True, blank=True, help_text="Future reservation integration")
    
    order_number = models.CharField(max_length=50)
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.DINE_IN)
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentGateway.choices, default=PaymentGateway.CASH)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    delivery_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_orders')
    
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        ordering = ['-created_at']
        unique_together = ('business', 'order_number')

    # Method: __str__
    def __str__(self):
        return f"Order {self.order_number}"


# Class: OrderItem
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Method: __str__
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.order_number})"


# Class: Payment
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    gateway = models.CharField(max_length=20, choices=PaymentGateway.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Class: Meta
    class Meta:
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"Payment {self.id} for Order {self.order.order_number}"


# Class: Invoice
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=100, unique=True)
    invoice_pdf = models.FileField(upload_to='invoices/', blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    # Method: __str__
    def __str__(self):
        return f"Invoice {self.invoice_number}"


# Class: Sale
class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='sale')
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)
    branch = models.ForeignKey('business.Branch', on_delete=models.CASCADE)
    sale_date = models.DateField(auto_now_add=True)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    tax_collected = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # Class: Meta
    class Meta:
        ordering = ['-sale_date']

    # Method: __str__
    def __str__(self):
        return f"Sale for Order {self.order.order_number}"


# Class: LoyaltyTransaction
class LoyaltyTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='loyalty_earned')
    points = models.IntegerField(help_text="Positive for earned, negative for redeemed")
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # Class: Meta
    class Meta:
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"{self.points} points for {self.customer}"


# Class: Delivery
class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_address = models.TextField()
    delivery_person_id = models.UUIDField(null=True, blank=True, help_text="Future integration with delivery tracking")
    status = models.CharField(max_length=50, default='PENDING')
    dispatched_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Method: __str__
    def __str__(self):
        return f"Delivery for Order {self.order.order_number}"
