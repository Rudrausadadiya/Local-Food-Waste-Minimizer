import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class NotificationChannel(models.TextChoices):
    IN_APP = 'IN_APP', _('In-App')
    EMAIL = 'EMAIL', _('Email')
    SMS = 'SMS', _('SMS')
    PUSH = 'PUSH', _('Push Notification')
    WEBHOOK = 'WEBHOOK', _('Webhook')

class NotificationStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    SENT = 'SENT', _('Sent')
    FAILED = 'FAILED', _('Failed')
    SCHEDULED = 'SCHEDULED', _('Scheduled')

class NotificationPriority(models.TextChoices):
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')
    URGENT = 'URGENT', _('Urgent')

class DigestMode(models.TextChoices):
    IMMEDIATE = 'IMMEDIATE', _('Immediate')
    HOURLY = 'HOURLY', _('Hourly')
    DAILY = 'DAILY', _('Daily')

class NotificationCategory(models.TextChoices):
    AUTHENTICATION = 'AUTHENTICATION', _('Authentication')
    BUSINESS = 'BUSINESS', _('Business')
    INVENTORY = 'INVENTORY', _('Inventory')
    ORDERS = 'ORDERS', _('Orders')
    RESERVATIONS = 'RESERVATIONS', _('Reservations')
    MARKETPLACE = 'MARKETPLACE', _('Marketplace')
    DONATIONS = 'DONATIONS', _('Donations')
    SYSTEM = 'SYSTEM', _('System')

class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preference')
    
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    digest_mode = models.CharField(max_length=20, choices=DigestMode.choices, default=DigestMode.IMMEDIATE)
    
    # Store JSON mapping of { "event_type": { "email": True, "sms": False } }
    per_event_preferences = models.JSONField(default=dict, blank=True)
    
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"


class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=NotificationCategory.choices, default=NotificationCategory.SYSTEM)
    event_type = models.CharField(max_length=100, unique=True, help_text="E.g., ORDER_CREATED")
    
    subject = models.CharField(max_length=255)
    body = models.TextField()
    variables = models.JSONField(default=list, blank=True, help_text="List of expected variables in the template")
    language = models.CharField(max_length=10, default='en')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Template: {self.name} ({self.language})"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    category = models.CharField(max_length=50, choices=NotificationCategory.choices, default=NotificationCategory.SYSTEM)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    priority = models.CharField(max_length=20, choices=NotificationPriority.choices, default=NotificationPriority.MEDIUM)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices, default=NotificationChannel.IN_APP)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    
    # Context
    related_object_type = models.CharField(max_length=100, blank=True, null=True)
    related_object_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Enhancements
    icon = models.CharField(max_length=255, blank=True, null=True, help_text="URL or identifier for icon")
    action_url = models.URLField(max_length=500, blank=True, null=True)
    action_text = models.CharField(max_length=100, blank=True, null=True)
    
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # For grouping duplicate logic
    group_key = models.CharField(max_length=255, blank=True, null=True, help_text="Hash to group similar notifications")
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} to {self.recipient.email}"


class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    provider = models.CharField(max_length=50, help_text="E.g., SendGrid, Twilio, FCM")
    
    request_payload = models.JSONField(blank=True, null=True)
    response_payload = models.JSONField(blank=True, null=True)
    
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    # Enhancements
    retry_count = models.PositiveIntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Log for {self.notification.id} via {self.provider}"
