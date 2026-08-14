import logging
import requests

logger = logging.getLogger(__name__)

# Class: WebhookProvider
class WebhookProvider:
    @staticmethod
    # Method: send
    def send(url: str, payload: dict) -> bool:
        """
        Dispatches a Webhook HTTP POST request to the specified URL.
        """
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Webhook delivered to {url} (status {response.status_code})")
            return True
        except requests.RequestException as e:
            logger.error(f"Webhook delivery to {url} failed: {e}")
            return False
