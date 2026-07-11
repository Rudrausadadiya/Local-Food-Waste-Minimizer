import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ExportFormat(models.TextChoices):
    CSV = 'CSV', 'CSV'
    EXCEL = 'EXCEL', 'Excel'
    PDF = 'PDF', 'PDF'
    JSON = 'JSON', 'JSON'

class ExportStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    COMPLETED = 'COMPLETED', _('Completed')
    FAILED = 'FAILED', _('Failed')

class ScheduleFrequency(models.TextChoices):
    DAILY = 'DAILY', _('Daily')
    WEEKLY = 'WEEKLY', _('Weekly')
    MONTHLY = 'MONTHLY', _('Monthly')

class AnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot_type = models.CharField(max_length=100, help_text="E.g., BUSINESS_KPI, GLOBAL_KPI")
    business_id = models.UUIDField(null=True, blank=True)
    branch_id = models.UUIDField(null=True, blank=True)
    data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Snapshot {self.snapshot_type} at {self.timestamp}"


class ScheduledReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_reports')
    report_type = models.CharField(max_length=100, help_text="E.g., SALES_REPORT, INVENTORY_REPORT")
    
    frequency = models.CharField(max_length=20, choices=ScheduleFrequency.choices, default=ScheduleFrequency.WEEKLY)
    export_format = models.CharField(max_length=10, choices=ExportFormat.choices, default=ExportFormat.CSV)
    
    filters = models.JSONField(default=dict, blank=True)
    recipients = models.JSONField(default=list, help_text="List of email addresses")
    
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.report_type} for {self.user.email} ({self.frequency})"


class AnalyticsExportLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='exports')
    report_name = models.CharField(max_length=255)
    export_format = models.CharField(max_length=10, choices=ExportFormat.choices)
    
    filters_applied = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=ExportStatus.choices, default=ExportStatus.PENDING)
    
    # Enhancements
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")
    download_count = models.PositiveIntegerField(default=0)
    
    error_message = models.TextField(blank=True, null=True)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_name} ({self.export_format}) - {self.status}"
