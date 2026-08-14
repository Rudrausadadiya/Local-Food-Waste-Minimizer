import requests
from datetime import time, datetime, timezone as dt_timezone
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core import mail

from apps.notifications.validators import validate_quiet_hours, is_channel_enabled
from apps.notifications.email import EmailProvider
from apps.notifications.webhook import WebhookProvider

# Class: MockPreference
class MockPreference:
    # Method: __init__
    def __init__(self, quiet_hours_start=None, quiet_hours_end=None, email_enabled=True, sms_enabled=True, push_enabled=True, per_event_preferences=None):
        self.quiet_hours_start = quiet_hours_start
        self.quiet_hours_end = quiet_hours_end
        self.email_enabled = email_enabled
        self.sms_enabled = sms_enabled
        self.push_enabled = push_enabled
        self.per_event_preferences = per_event_preferences or {}

# Class: NotificationValidatorsTestCase
class NotificationValidatorsTestCase(TestCase):
    # Method: test_quiet_hours
    def test_quiet_hours(self):
        pref = MockPreference(quiet_hours_start=time(22, 0), quiet_hours_end=time(8, 0))
        
        dt_during = datetime(2026, 7, 26, 23, 0, 0, tzinfo=dt_timezone.utc)
        self.assertTrue(validate_quiet_hours(pref, scheduled_at=dt_during))
        
        dt_outside = datetime(2026, 7, 26, 14, 0, 0, tzinfo=dt_timezone.utc)
        self.assertFalse(validate_quiet_hours(pref, scheduled_at=dt_outside))

    # Method: test_channel_enabled
    def test_channel_enabled(self):
        pref = MockPreference(
            email_enabled=True,
            sms_enabled=False,
            per_event_preferences={'order_created': {'email': True, 'sms': False}}
        )
        self.assertTrue(is_channel_enabled(pref, channel='EMAIL', event_type='order_created'))
        self.assertFalse(is_channel_enabled(pref, channel='SMS', event_type='order_created'))

# Class: NotificationProvidersTestCase
class NotificationProvidersTestCase(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    # Method: test_email_provider_success
    def test_email_provider_success(self):
        result = EmailProvider.send(
            recipient="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])

    @patch("apps.notifications.email.send_mail", side_effect=Exception("SMTP Connection Error"))
    # Method: test_email_provider_failure
    def test_email_provider_failure(self, mock_send_mail):
        result = EmailProvider.send(
            recipient="fail@example.com",
            subject="Fail Subject",
            body="Fail Body"
        )
        self.assertFalse(result)

    @patch("requests.post")
    # Method: test_webhook_provider_success
    def test_webhook_provider_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = WebhookProvider.send("https://example.com/webhook", {"event": "order_created"})
        self.assertTrue(result)
        mock_post.assert_called_once_with("https://example.com/webhook", json={"event": "order_created"}, timeout=5)

    @patch("requests.post", side_effect=requests.RequestException("Connection refused"))
    # Method: test_webhook_provider_failure
    def test_webhook_provider_failure(self, mock_post):
        result = WebhookProvider.send("https://example.com/webhook", {"event": "order_created"})
        self.assertFalse(result)
