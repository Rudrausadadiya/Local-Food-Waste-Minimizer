from typing import Dict, Any, List
from django.utils import timezone
from django.db import transaction
from .models import (
    Notification, NotificationChannel, NotificationStatus,
    NotificationPriority, DigestMode
)
from .repositories import (
    NotificationRepository, NotificationPreferenceRepository, 
    NotificationTemplateRepository, NotificationLogRepository
)
from .validators import validate_quiet_hours, is_channel_enabled
from .templates import TemplateRenderer
from .email import EmailProvider
from .sms import SMSProvider
from .push import PushProvider
from .webhook import WebhookProvider

# Class: NotificationPriorityService
class NotificationPriorityService:
    @staticmethod
    # Method: calculate_priority
    def calculate_priority(event_type: str, recipient) -> str:
        # Future AI placeholder logic implementation
        critical_events = ['ORDER_CREATED', 'RESERVATION_CONFIRMED', 'DONATION_APPROVED']
        high_events = ['ORDER_CANCELLED', 'DONATION_REQUESTED']
        
        if event_type in critical_events:
            return NotificationPriority.URGENT
        elif event_type in high_events:
            return NotificationPriority.HIGH
            
        return NotificationPriority.MEDIUM


# Class: NotificationService
class NotificationService:
    @staticmethod
    @transaction.atomic
    # Method: dispatch_event
    def dispatch_event(user, event_type: str, context: Dict[str, Any], related_object=None, channels: List[str] = None):
        """
        Main entry point for generating notifications from signals.
        """
        pref = NotificationPreferenceRepository.get_or_create(user)
        template = NotificationTemplateRepository.get_by_event(event_type)
        
        if not template:
            return None
            
        # Group duplicates based on event and related object
        related_type = related_object.__class__.__name__ if related_object else None
        related_id = str(related_object.id) if related_object else None
        group_key = f"{event_type}_{related_type}_{related_id}"
        
        if NotificationRepository.check_duplicate(user, group_key):
            return None # Skip duplicate
            
        subject = TemplateRenderer.render(template.subject, context)
        body = TemplateRenderer.render(template.body, context)
        priority = NotificationPriorityService.calculate_priority(event_type, user)
        
        if not channels:
            channels = [c for c, _ in NotificationChannel.choices]
            
        created_notifications = []
        for channel in channels:
            if not is_channel_enabled(pref, channel, event_type):
                continue
                
            scheduled_at = None
            if validate_quiet_hours(pref):
                # Defer to end of quiet hours
                scheduled_at = timezone.now().replace(
                    hour=pref.quiet_hours_end.hour,
                    minute=pref.quiet_hours_end.minute
                )
                if scheduled_at < timezone.now():
                    scheduled_at += timezone.timedelta(days=1)
            
            # Handle Digest Modes by pushing scheduled_at to next interval
            if pref.digest_mode == DigestMode.HOURLY and not scheduled_at:
                now = timezone.now()
                scheduled_at = now.replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)
            elif pref.digest_mode == DigestMode.DAILY and not scheduled_at:
                now = timezone.now()
                scheduled_at = now.replace(hour=8, minute=0, second=0, microsecond=0) + timezone.timedelta(days=1)
                
            status = NotificationStatus.SCHEDULED if scheduled_at else NotificationStatus.PENDING
            
            notif = NotificationRepository.create({
                'recipient': user,
                'category': template.category,
                'title': subject,
                'message': body,
                'priority': priority,
                'channel': channel,
                'status': status,
                'related_object_type': related_type,
                'related_object_id': related_id,
                'scheduled_at': scheduled_at,
                'group_key': group_key
            })
            created_notifications.append(notif)
            
        return created_notifications

    @staticmethod
    # Method: process_queue
    def process_queue(limit: int = 100):
        """
        Intended for Celery beat: Grabs pending notifications and sends them.
        """
        notifications = NotificationRepository.get_pending_notifications(limit)
        for notif in notifications:
            NotificationService._send_single(notif)

    @staticmethod
    # Method: _send_single
    def _send_single(notification: Notification):
        success = False
        error_msg = ""
        provider_name = ""
        
        try:
            if notification.channel == NotificationChannel.EMAIL:
                provider_name = "SendGrid"
                success = EmailProvider.send(notification.recipient.email, notification.title, notification.message)
            elif notification.channel == NotificationChannel.SMS:
                provider_name = "Twilio"
                phone = getattr(notification.recipient, 'phone', '0000000000')
                success = SMSProvider.send(phone, notification.message)
            elif notification.channel == NotificationChannel.PUSH:
                provider_name = "FCM"
                device_token = "dummy_token" # Usually fetched from a Device table
                success = PushProvider.send(device_token, notification.title, notification.message)
            elif notification.channel == NotificationChannel.WEBHOOK:
                provider_name = "Webhook"
                success = WebhookProvider.send("https://api.example.com/webhook", {"title": notification.title, "message": notification.message})
            elif notification.channel == NotificationChannel.IN_APP:
                provider_name = "Internal"
                success = True # In app is instantly delivered conceptually via DB
        except Exception as e:
            success = False
            error_msg = str(e)
            
        NotificationLogRepository.create({
            'notification': notification,
            'channel': notification.channel,
            'provider': provider_name,
            'success': success,
            'error_message': error_msg,
            'delivered_at': timezone.now() if success else None
        })
        
        updates = {
            'status': NotificationStatus.SENT if success else NotificationStatus.FAILED
        }
        if success:
            updates['sent_at'] = timezone.now()
            
        NotificationRepository.update(notification, updates)
        return success

    @staticmethod
    # Method: retry_failed
    def retry_failed():
        """
        Retry failed deliveries up to 3 times.
        """
        failed_notifs = NotificationRepository.get_failed_notifications()
        for notif in failed_notifs:
            logs = notif.logs.all()
            if logs.count() < 3:
                # Add retry count explicitly for the log
                NotificationService._send_single(notif)
            else:
                NotificationRepository.update(notif, {'is_archived': True})

    @staticmethod
    # Method: mark_as_read
    def mark_as_read(notification_id: str, user):
        notif = NotificationRepository.get_by_id(notification_id)
        if notif and notif.recipient == user:
            NotificationRepository.update(notif, {'read_at': timezone.now()})
            # Also update log opened_at if IN_APP
            log = notif.logs.filter(channel=NotificationChannel.IN_APP).first()
            if log and not log.opened_at:
                NotificationLogRepository.update(log, {'opened_at': timezone.now()})
            return notif
        return None

# Class: NotificationPreferenceService
class NotificationPreferenceService:
    @staticmethod
    # Method: update_preferences
    def update_preferences(user, data: Dict[str, Any]):
        pref = NotificationPreferenceRepository.get_or_create(user)
        return NotificationPreferenceRepository.update(pref, data)
