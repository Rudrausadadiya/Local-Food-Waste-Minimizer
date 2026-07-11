from django.dispatch import Signal

# Order Signals
order_created = Signal()
order_completed = Signal()
order_cancelled = Signal()

# Payment Signals
payment_completed = Signal()
payment_failed = Signal()
refund_completed = Signal()

# Invoice Signals
invoice_generated = Signal()

# Inventory Signals
inventory_reserved = Signal()
inventory_released = Signal()
