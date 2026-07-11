import logging

logger = logging.getLogger(__name__)

class EmailProvider:
    @staticmethod
    def send(recipient: str, subject: str, body: str) -> bool:
        """
        Placeholder for SendGrid/SMTP integration.
        """
        logger.info(f"Simulating sending Email to {recipient} with subject: {subject}")
        # Return True for success
        return True
