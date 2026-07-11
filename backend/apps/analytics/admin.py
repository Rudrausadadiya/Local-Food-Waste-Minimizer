from django.contrib import admin
from .models import AnalyticsSnapshot, ScheduledReport, AnalyticsExportLog

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('snapshot_type', 'business_id', 'branch_id', 'timestamp')
    list_filter = ('snapshot_type', 'timestamp')
    search_fields = ('snapshot_type',)
    readonly_fields = ('id', 'timestamp')

@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'user', 'frequency', 'export_format', 'is_active', 'next_run_at')
    list_filter = ('frequency', 'export_format', 'is_active')
    search_fields = ('report_type', 'user__email')

@admin.register(AnalyticsExportLog)
class AnalyticsExportLogAdmin(admin.ModelAdmin):
    list_display = ('report_name', 'user', 'export_format', 'status', 'created_at')
    list_filter = ('export_format', 'status')
    search_fields = ('report_name', 'user__email')
    readonly_fields = ('id', 'created_at', 'completed_at', 'file_size', 'download_count')
