import django_filters
from .models import ScheduledReport, AnalyticsExportLog

# Class: ScheduledReportFilter
class ScheduledReportFilter(django_filters.FilterSet):
    # Class: Meta
    class Meta:
        model = ScheduledReport
        fields = ['report_type', 'frequency', 'is_active']

# Class: AnalyticsExportLogFilter
class AnalyticsExportLogFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Class: Meta
    class Meta:
        model = AnalyticsExportLog
        fields = ['report_name', 'export_format', 'status']
