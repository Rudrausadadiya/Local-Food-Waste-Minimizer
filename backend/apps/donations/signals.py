from django.dispatch import Signal

# Lifecycle Signals
ngo_registered = Signal()
ngo_verified = Signal()
donation_listed = Signal()
donation_requested = Signal()
donation_approved = Signal()
pickup_scheduled = Signal()
donation_completed = Signal()
donation_expired = Signal()

# Custom Event Signals
donation_expiring = Signal()
pickup_reminder = Signal()
pickup_delayed = Signal()
impact_calculated = Signal()
