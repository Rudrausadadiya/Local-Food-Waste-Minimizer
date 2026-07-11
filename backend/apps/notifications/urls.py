from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register(r'inbox', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notificationpreference')
router.register(r'templates', NotificationTemplateViewSet, basename='notificationtemplate')

urlpatterns = [
    path('', include(router.urls)),
]
