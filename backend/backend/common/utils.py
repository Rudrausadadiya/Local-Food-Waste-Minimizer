import logging

def get_logger(name):
    """
    Utility function to get a configured logger.
    """
    return logging.getLogger(name)

# Add other common utilities here as needed, such as:
# - Caching helpers
# - Common validators
# - Third-party service integrations (S3, Email, etc.)
