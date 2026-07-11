from django.dispatch import Signal

# Reservation Lifecycle Signals
reservation_created = Signal()
reservation_confirmed = Signal()
reservation_cancelled = Signal()
reservation_completed = Signal()
reservation_expired = Signal()
reservation_converted_to_order = Signal()

# Custom Event Signals
reservation_reminder_due = Signal()
reservation_no_show = Signal()
