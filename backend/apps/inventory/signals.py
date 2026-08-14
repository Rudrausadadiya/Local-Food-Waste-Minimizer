from django.dispatch import Signal
from django.dispatch import receiver

# Define custom signals
stock_updated = Signal()  # args: inventory, transaction, quantity_change
batch_expired = Signal()  # args: batch
waste_recorded = Signal() # args: waste_record
low_stock = Signal()      # args: inventory

# Signal Receivers for future ML and Analytics hooks

@receiver(stock_updated)
# Function: handle_stock_updated
def handle_stock_updated(sender, inventory, transaction, quantity_change, **kwargs):
    """
    Hook for triggering analytics updates and potential machine learning 
    demand forecasting model updates when stock changes.
    """
    # In future: Push to Kafka/RabbitMQ or call Analytics service async
    pass

@receiver(batch_expired)
# Function: handle_batch_expired
def handle_batch_expired(sender, batch, **kwargs):
    """
    Hook for analytics: Tracking expiry patterns over time to optimize purchasing.
    """
    pass

@receiver(waste_recorded)
# Function: handle_waste_recorded
def handle_waste_recorded(sender, waste_record, **kwargs):
    """
    Hook for analytics: Identifying branches/products with high waste rates.
    """
    pass

@receiver(low_stock)
# Function: handle_low_stock
def handle_low_stock(sender, inventory, **kwargs):
    """
    Hook for automated reordering systems and alerting.
    """
    pass
