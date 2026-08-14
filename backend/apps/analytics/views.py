from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse

from .models import ScheduledReport, AnalyticsExportLog
from .serializers import ScheduledReportSerializer, AnalyticsExportLogSerializer
from .services import DashboardService, ReportService, DataQualityService, DatasetService
from .filters import ScheduledReportFilter, AnalyticsExportLogFilter
from .permissions import IsAnalyticsViewer, IsAnalyticsAdmin

# Class: DashboardViewSet
class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAnalyticsViewer]

    # Method: list
    def list(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        business_id = request.query_params.get('business_id')
        
        # Default to last 30 days if not provided
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=30)
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
        kpis = DashboardService.get_dashboard_summary(start_date, end_date, business_id)
        return Response(kpis)

    @action(detail=False, methods=['get'])
    # Method: data_quality
    def data_quality(self, request):
        business_id = request.query_params.get('business_id')
        anomalies = DataQualityService.detect_anomalies(business_id)
        return Response(anomalies)


# Class: ReportViewSet
class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAnalyticsViewer]

    @action(detail=False, methods=['get'])
    # Method: download
    def download(self, request):
        report_type = request.query_params.get('report_type', 'SALES')
        export_format = request.query_params.get('export_format', 'CSV')
        business_id = request.query_params.get('business_id')
        start_date = request.query_params.get('start_date', timezone.now() - timezone.timedelta(days=30))
        end_date = request.query_params.get('end_date', timezone.now())
        
        # In a real app this would be Celery dispatched. 
        # Here we do it synchronously to fulfill the placeholder logic immediately.
        file_content = ReportService.generate_report(report_type, start_date, end_date, export_format, business_id)
        
        # Log it
        from .repositories import AnalyticsExportLogRepository
        from .models import ExportStatus
        AnalyticsExportLogRepository.create({
            'user': request.user,
            'report_name': report_type,
            'export_format': export_format,
            'status': ExportStatus.COMPLETED,
            'file_name': f"{report_type}_{timezone.now().timestamp()}.{export_format.lower()}",
            'file_size': len(file_content.encode('utf-8'))
        })

        content_type = 'text/csv' if export_format == 'CSV' else 'application/json'
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{report_type}.{export_format.lower()}"'
        return response

    @action(detail=False, methods=['get'], permission_classes=[IsAnalyticsAdmin])
    # Method: ml_dataset
    def ml_dataset(self, request):
        model_type = request.query_params.get('model_type', 'FORECAST')
        business_id = request.query_params.get('business_id')
        dataset = DatasetService.extract_training_dataset(model_type, business_id)
        
        response = HttpResponse(dataset, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="dataset_{model_type}.csv"'
        return response


# Class: ScheduledReportViewSet
class ScheduledReportViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAnalyticsViewer]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ScheduledReportFilter

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ScheduledReport.objects.none()
        if getattr(user, 'role', None) == 'ADMIN' and 'all' in self.request.query_params:
            return ScheduledReport.objects.all()
        return ScheduledReport.objects.filter(user=user)

    # Method: perform_create
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Class: AnalyticsExportLogViewSet
class AnalyticsExportLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AnalyticsExportLogSerializer
    permission_classes = [IsAnalyticsViewer]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyticsExportLogFilter

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return AnalyticsExportLog.objects.none()
        if getattr(user, 'role', None) == 'ADMIN' and 'all' in self.request.query_params:
            return AnalyticsExportLog.objects.all()
        return AnalyticsExportLog.objects.filter(user=user)
