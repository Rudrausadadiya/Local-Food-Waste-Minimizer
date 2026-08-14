import logging

logger = logging.getLogger(__name__)

# Class: PushProvider
class PushProvider:
    @staticmethod
    # Method: send
    def send(device_token: str, title: str, message: str, data: dict = None) -> bool:
        """
        Simulated Push provider for Firebase Cloud Messaging (FCM) integration.
        NOTE: Intentionally simulated in this demonstration environment to avoid requiring
        paid FCM service account JSON credentials. The NotificationService dispatch architecture
        is fully modular so swapping in `firebase_admin.messaging` requires changes only in this file.
        """
        logger.info(f"Simulating sending Push to {device_token} - Title: {title}")
        return True
