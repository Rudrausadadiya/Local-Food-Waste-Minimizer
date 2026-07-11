from rest_framework import serializers
from .models import AnalyticsSnapshot, ScheduledReport, AnalyticsExportLog

class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')

class ScheduledReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReport
        fields = '__all__'
        read_only_fields = ('id', 'user', 'last_run_at', 'created_at', 'updated_at')

class AnalyticsExportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsExportLog
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'completed_at', 'file_size', 'download_count')
