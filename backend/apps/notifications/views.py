from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Notification, NotificationPreference, NotificationTemplate
from .serializers import NotificationSerializer, NotificationPreferenceSerializer, NotificationTemplateSerializer
from .services import NotificationService, NotificationPreferenceService
from .filters import NotificationFilter
from .permissions import IsNotificationOwnerOrAdmin, IsAdminUser

# Class: NotificationViewSet
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Inbox view for users.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsNotificationOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NotificationFilter
    search_fields = ['title', 'message', 'action_text']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()
        if getattr(user, 'role', None) == 'ADMIN' and 'all' in self.request.query_params:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=user, is_archived=False)

    @action(detail=True, methods=['post'])
    # Method: mark_as_read
    def mark_as_read(self, request, pk=None):
        notif = NotificationService.mark_as_read(str(pk), request.user)
        if notif:
            return Response(self.get_serializer(notif).data)
        return Response({'detail': 'Not found or forbidden.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    # Method: mark_all_as_read
    def mark_all_as_read(self, request):
        qs = self.get_queryset().filter(read_at__isnull=True)
        count = qs.count()
        qs.update(read_at=timezone.now())
        return Response({'marked_count': count})


# Class: NotificationPreferenceViewSet
class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsNotificationOwnerOrAdmin]
    
    # Method: get_queryset
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return NotificationPreference.objects.none()
        if getattr(user, 'role', None) == 'ADMIN' and 'all' in self.request.query_params:
            return NotificationPreference.objects.all()
        return NotificationPreference.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    # Method: me
    def me(self, request):
        from .repositories import NotificationPreferenceRepository
        pref = NotificationPreferenceRepository.get_or_create(request.user)
        return Response(self.get_serializer(pref).data)

    @action(detail=False, methods=['patch'])
    # Method: update_me
    def update_me(self, request):
        pref = NotificationPreferenceService.update_preferences(request.user, request.data)
        return Response(self.get_serializer(pref).data)


# Class: NotificationTemplateViewSet
class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'event_type', 'subject']
