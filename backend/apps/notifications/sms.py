import logging

logger = logging.getLogger(__name__)

# Class: SMSProvider
class SMSProvider:
    @staticmethod
    # Method: send
    def send(phone_number: str, message: str) -> bool:
        """
        Simulated SMS provider for Twilio / WhatsApp Business integration.
        NOTE: Intentionally simulated in this demonstration environment to avoid requiring
        paid Twilio/WhatsApp API key credentials. The NotificationService dispatch architecture
        is fully modular so swapping in `twilio.rest.Client` requires changes only in this file.
        """
        logger.info(f"Simulating sending SMS to {phone_number}: {message}")
        return True
