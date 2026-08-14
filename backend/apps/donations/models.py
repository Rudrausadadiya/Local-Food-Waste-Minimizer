import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Class: NGOVerificationStatus
class NGOVerificationStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    VERIFIED = 'VERIFIED', _('Verified')
    REJECTED = 'REJECTED', _('Rejected')

# Class: DonationStatus
class DonationStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', _('Active')
    REQUESTED = 'REQUESTED', _('Requested')
    RESERVED = 'RESERVED', _('Reserved')
    COMPLETED = 'COMPLETED', _('Completed')
    EXPIRED = 'EXPIRED', _('Expired')

# Class: DonationRequestStatus
class DonationRequestStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    PARTIALLY_APPROVED = 'PARTIALLY_APPROVED', _('Partially Approved')
    REJECTED = 'REJECTED', _('Rejected')
    CANCELLED = 'CANCELLED', _('Cancelled')

# Class: PickupStatus
class PickupStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', _('Scheduled')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    COMPLETED = 'COMPLETED', _('Completed')
    MISSED = 'MISSED', _('Missed')

# Class: Priority
class Priority(models.TextChoices):
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')
    CRITICAL = 'CRITICAL', _('Critical')

# Class: NGO
class NGO(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ngo_profile')
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    verification_status = models.CharField(max_length=20, choices=NGOVerificationStatus.choices, default=NGOVerificationStatus.PENDING)
    service_radius = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'), help_text="Service radius in km")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Method: __str__
    def __str__(self):
        return f"{self.organization_name} ({self.verification_status})"

# Class: NGODocument
class NGODocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='ngo_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Method: __str__
    def __str__(self):
        return f"{self.document_name} for {self.ngo.organization_name}"

# Class: DonationListing
class DonationListing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='donation_listings')
    branch = models.ForeignKey('business.Branch', on_delete=models.CASCADE, related_name='donation_listings')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='donation_listings')
    inventory_batch = models.ForeignKey('inventory.InventoryBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='donation_listings')
    
    quantity = models.PositiveIntegerField()
    donation_status = models.CharField(max_length=20, choices=DonationStatus.choices, default=DonationStatus.ACTIVE)
    
    available_until = models.DateTimeField()
    pickup_window_start = models.DateTimeField()
    pickup_window_end = models.DateTimeField()
    
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    visible_to_verified_ngos = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        ordering = ['-priority', '-created_at']

    # Method: __str__
    def __str__(self):
        return f"Donation: {self.quantity}x {self.product.name} ({self.donation_status})"

# Class: DonationRequest
class DonationRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_listing = models.ForeignKey(DonationListing, on_delete=models.CASCADE, related_name='requests')
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='donation_requests')
    
    request_status = models.CharField(max_length=20, choices=DonationRequestStatus.choices, default=DonationRequestStatus.PENDING)
    requested_quantity = models.PositiveIntegerField()
    request_message = models.TextField(blank=True, null=True)
    approved_quantity = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Class: Meta
    class Meta:
        unique_together = ('donation_listing', 'ngo')
        ordering = ['-created_at']

    # Method: __str__
    def __str__(self):
        return f"Request by {self.ngo.organization_name} for {self.donation_listing}"

# Class: DonationPickup
class DonationPickup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_request = models.OneToOneField(DonationRequest, on_delete=models.CASCADE, related_name='pickup')
    pickup_status = models.CharField(max_length=20, choices=PickupStatus.choices, default=PickupStatus.SCHEDULED)
    
    pickup_time = models.DateTimeField(null=True, blank=True)
    collected_by = models.CharField(max_length=255, help_text="Name of the person collecting")
    proof_image = models.ImageField(upload_to='donation_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Method: __str__
    def __str__(self):
        return f"Pickup for {self.donation_request}"

# Class: PickupRoute
class PickupRoute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name='pickup_routes')
    pickups = models.ManyToManyField(DonationPickup, related_name='routes', blank=True)
    marketplace_orders = models.ManyToManyField('marketplace.MarketplaceOrder', related_name='pickup_routes', blank=True)
    route_date = models.DateField()
    driver_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Method: __str__
    def __str__(self):
        return f"Route for {self.ngo} on {self.route_date}"

# Class: DonationHistory
class DonationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_listing = models.ForeignKey(DonationListing, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20, choices=DonationStatus.choices, blank=True, null=True)
    new_status = models.CharField(max_length=20, choices=DonationStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    # Class: Meta
    class Meta:
        ordering = ['-changed_at']

    # Method: __str__
    def __str__(self):
        return f"{self.donation_listing}: {self.previous_status} -> {self.new_status}"

# Class: DonationImpact
class DonationImpact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_pickup = models.OneToOneField(DonationPickup, on_delete=models.CASCADE, related_name='impact', null=True, blank=True)
    marketplace_order = models.OneToOneField('marketplace.MarketplaceOrder', on_delete=models.CASCADE, related_name='impact', null=True, blank=True)
    
    meals_served = models.PositiveIntegerField(default=0)
    food_saved_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    carbon_saved_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    beneficiaries = models.PositiveIntegerField(default=0)
    
    calculated_at = models.DateTimeField(auto_now_add=True)

    # Method: __str__
    def __str__(self):
        return f"Impact for {self.donation_pickup}"
