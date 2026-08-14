import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# Class: EmailProvider
class EmailProvider:
    @staticmethod
    # Method: send
    def send(recipient: str, subject: str, body: str) -> bool:
        """
        Sends an email using Django's built-in mail framework.
        Defaults to console backend in dev and SMTP in production.
        """
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localfoodwaste.example'),
                recipient_list=[recipient],
                fail_silently=False,
            )
            logger.info(f"Email sent to {recipient} with subject: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False
