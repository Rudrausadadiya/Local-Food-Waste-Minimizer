from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, ReportViewSet, ScheduledReportViewSet, AnalyticsExportLogViewSet

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'schedules', ScheduledReportViewSet, basename='scheduledreport')
router.register(r'exports', AnalyticsExportLogViewSet, basename='analyticsexportlog')

urlpatterns = [
    path('', include(router.urls)),
]
