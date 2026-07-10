from django.db import models
from django.conf import settings
from django.utils import timezone
from common.models import UUIDTimeStampedModel
import uuid

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

class Business(UUIDTimeStampedModel):
    class BusinessType(models.TextChoices):
        VENDOR = 'VENDOR', 'Vendor'
        NGO = 'NGO', 'NGO'
        CORPORATE = 'CORPORATE', 'Corporate'
        RETAIL = 'RETAIL', 'Retail'

    class BusinessStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='businesses')
    business_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    business_type = models.CharField(max_length=50, choices=BusinessType.choices)
    business_status = models.CharField(max_length=50, choices=BusinessStatus.choices, default=BusinessStatus.PENDING)
    
    business_email = models.EmailField(unique=True)
    business_phone = models.CharField(max_length=20)
    
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    
    logo = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=10, default='USD')
    language = models.CharField(max_length=10, default='en')
    
    subscription_plan = models.CharField(max_length=100, blank=True, null=True)
    subscription_expiry = models.DateTimeField(blank=True, null=True)
    
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    objects = models.Manager() # Default manager
    available_objects = SoftDeleteManager()
    active_objects = ActiveManager()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        # Audit hook placeholder
        # e.g., AuditService.log_change(self)
        super().save(*args, **kwargs)

class Address(UUIDTimeStampedModel):
    class AddressType(models.TextChoices):
        BILLING = 'BILLING', 'Billing'
        SHIPPING = 'SHIPPING', 'Shipping'
        OPERATIONAL = 'OPERATIONAL', 'Operational'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=AddressType.choices, default=AddressType.OPERATIONAL)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}"

class Branch(UUIDTimeStampedModel):
    class BranchStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        CLOSED = 'CLOSED', 'Closed'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='branches')
    branch_name = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=50, unique=True)
    is_main_branch = models.BooleanField(default=False)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_branches')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    branch_status = models.CharField(max_length=20, choices=BranchStatus.choices, default=BranchStatus.ACTIVE)
    opening_date = models.DateField(blank=True, null=True)
    closing_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.branch_name

class OperatingHours(UUIDTimeStampedModel):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='operating_hours')
    weekday = models.IntegerField(choices=Weekday.choices)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('business', 'weekday')

    def __str__(self):
        return f"{self.business.business_name} - {self.get_weekday_display()}"
