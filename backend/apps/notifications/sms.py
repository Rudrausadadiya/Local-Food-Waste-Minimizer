import logging

logger = logging.getLogger(__name__)

class SMSProvider:
    @staticmethod
    def send(phone_number: str, message: str) -> bool:
        """
        Placeholder for Twilio/WhatsApp Business integration.
        """
        logger.info(f"Simulating sending SMS to {phone_number}: {message}")
        # Return True for success
        return True
