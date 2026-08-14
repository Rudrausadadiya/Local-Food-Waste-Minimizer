import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Class: ReservationType
class ReservationType(models.TextChoices):
    TABLE = 'TABLE', _('Table')
    PRODUCT = 'PRODUCT', _('Product')
    EVENT = 'EVENT', _('Event')

# Class: ReservationStatus
class ReservationStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    CANCELLED = 'CANCELLED', _('Cancelled')
    COMPLETED = 'COMPLETED', _('Completed')
    EXPIRED = 'EXPIRED', _('Expired')

# Class: AdvancePaymentStatus
class AdvancePaymentStatus(models.TextChoices):
    NOT_REQUIRED = 'NOT_REQUIRED', _('Not Required')
    PENDING = 'PENDING', _('Pending')
    PAID = 'PAID', _('Paid')
    REFUNDED = 'REFUNDED', _('Refunded')

# Class: Table
class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='tables')
    branch = models.ForeignKey('business.Branch', on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        unique_together = ('branch', 'table_number')
        ordering = ['table_number']

    # Method: __str__
    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats)"


# Class: Reservation
class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='reservations')
    branch = models.ForeignKey('business.Branch', on_delete=models.CASCADE, related_name='reservations')
    customer = models.ForeignKey('orders.Customer', on_delete=models.CASCADE, related_name='reservations')
    
    reservation_number = models.CharField(max_length=50)
    reservation_type = models.CharField(max_length=20, choices=ReservationType.choices, default=ReservationType.TABLE)
    reservation_status = models.CharField(max_length=20, choices=ReservationStatus.choices, default=ReservationStatus.PENDING)
    
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    expected_duration = models.DurationField(help_text="Expected duration of the reservation")
    party_size = models.PositiveIntegerField(default=1)
    
    # Optional Fields
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    advance_payment_status = models.CharField(max_length=20, choices=AdvancePaymentStatus.choices, default=AdvancePaymentStatus.NOT_REQUIRED)
    reservation_source = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., Web, Phone, Walk-in, App")
    expected_arrival = models.DateTimeField(blank=True, null=True)
    actual_arrival = models.DateTimeField(blank=True, null=True)
    no_show = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_reservations')
    
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        unique_together = ('business', 'reservation_number')
        ordering = ['-reservation_date', '-reservation_time']

    # Method: __str__
    def __str__(self):
        return f"Reservation {self.reservation_number}"


# Class: ReservationItem
class ReservationItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='reservation_items')
    quantity = models.PositiveIntegerField(default=1)
    reserved_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Method: __str__
    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Res: {self.reservation.reservation_number})"


# Class: ReservationTable
class ReservationTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='reserved_tables')
    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='reservations')

    # Method: __str__
    def __str__(self):
        return f"{self.table} for {self.reservation}"


# Class: ReservationHistory
class ReservationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20, choices=ReservationStatus.choices, blank=True, null=True)
    new_status = models.CharField(max_length=20, choices=ReservationStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    # Class: Meta
    class Meta:
        ordering = ['-changed_at']

    # Method: __str__
    def __str__(self):
        return f"{self.reservation.reservation_number}: {self.previous_status} -> {self.new_status}"
