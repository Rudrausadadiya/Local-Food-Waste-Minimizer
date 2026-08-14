from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.utils import timezone
from .models import (
    Notification, NotificationPreference, NotificationTemplate, NotificationLog,
    NotificationStatus
)

# Class: NotificationRepository
class NotificationRepository:
    @staticmethod
    # Method: get_by_id
    def get_by_id(notification_id: str) -> Optional[Notification]:
        return Notification.objects.filter(id=notification_id).first()

    @staticmethod
    # Method: get_by_id_for_update
    def get_by_id_for_update(notification_id: str) -> Optional[Notification]:
        return Notification.objects.select_for_update().filter(id=notification_id).first()

    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> Notification:
        return Notification.objects.create(**data)

    @staticmethod
    # Method: update
    def update(notification: Notification, data: Dict[str, Any]) -> Notification:
        for key, value in data.items():
            setattr(notification, key, value)
        notification.save()
        return notification

    @staticmethod
    # Method: get_pending_notifications
    def get_pending_notifications(limit: int = 100) -> QuerySet:
        now = timezone.now()
        return Notification.objects.filter(
            status=NotificationStatus.PENDING,
            is_archived=False
        ).exclude(
            scheduled_at__gt=now
        ).order_by('-priority', 'created_at')[:limit]

    @staticmethod
    # Method: get_failed_notifications
    def get_failed_notifications(limit: int = 100) -> QuerySet:
        # Get notifications that failed but haven't exceeded retry logic max bounds
        return Notification.objects.filter(
            status=NotificationStatus.FAILED,
            is_archived=False
        ).order_by('-updated_at')[:limit]
        
    @staticmethod
    # Method: check_duplicate
    def check_duplicate(recipient, group_key, minutes: int = 60) -> bool:
        if not group_key:
            return False
        time_threshold = timezone.now() - timezone.timedelta(minutes=minutes)
        return Notification.objects.filter(
            recipient=recipient,
            group_key=group_key,
            created_at__gte=time_threshold
        ).exists()

# Class: NotificationPreferenceRepository
class NotificationPreferenceRepository:
    @staticmethod
    # Method: get_or_create
    def get_or_create(user) -> NotificationPreference:
        pref, _ = NotificationPreference.objects.get_or_create(user=user)
        return pref

    @staticmethod
    # Method: update
    def update(pref: NotificationPreference, data: Dict[str, Any]) -> NotificationPreference:
        for key, value in data.items():
            setattr(pref, key, value)
        pref.save()
        return pref

# Class: NotificationTemplateRepository
class NotificationTemplateRepository:
    @staticmethod
    # Method: get_by_event
    def get_by_event(event_type: str, language: str = 'en') -> Optional[NotificationTemplate]:
        return NotificationTemplate.objects.filter(event_type=event_type, language=language, is_active=True).first()

# Class: NotificationLogRepository
class NotificationLogRepository:
    @staticmethod
    # Method: create
    def create(data: Dict[str, Any]) -> NotificationLog:
        return NotificationLog.objects.create(**data)
        
    @staticmethod
    # Method: update
    def update(log: NotificationLog, data: Dict[str, Any]) -> NotificationLog:
        for key, value in data.items():
            setattr(log, key, value)
        log.save()
        return log
