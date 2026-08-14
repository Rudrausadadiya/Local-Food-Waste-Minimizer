from rest_framework import serializers
from .models import AnalyticsSnapshot, ScheduledReport, AnalyticsExportLog

# Class: AnalyticsSnapshotSerializer
class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')

# Class: ScheduledReportSerializer
class ScheduledReportSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = ScheduledReport
        fields = '__all__'
        read_only_fields = ('id', 'user', 'last_run_at', 'created_at', 'updated_at')

# Class: AnalyticsExportLogSerializer
class AnalyticsExportLogSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = AnalyticsExportLog
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'completed_at', 'file_size', 'download_count')
