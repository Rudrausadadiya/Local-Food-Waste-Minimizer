from django.dispatch import receiver
from django.db.models.signals import post_save

# The signal listeners will be fully implemented in a dedicated listener setup
# within services.py or this file.

# We will listen to external signals from:
# apps.users.signals
# apps.orders.signals
# apps.reservations.signals
# apps.marketplace.signals
# apps.inventory.signals
# apps.donations.signals

# For now, we prepare the structure to attach handlers to these signals.
def setup_signal_listeners():
    from apps.orders.signals import order_created
    from apps.reservations.signals import reservation_confirmed
    from apps.donations.signals import donation_approved
    from apps.marketplace.signals import listing_published
    from apps.notifications.services import NotificationService
    
    @receiver(order_created)
    def handle_order_created(sender, order, **kwargs):
        NotificationService.dispatch_event(
            user=order.customer.user,
            event_type='ORDER_CREATED',
            context={'order_number': order.order_number, 'total': str(order.total_amount)},
            related_object=order
        )

    @receiver(reservation_confirmed)
    def handle_reservation_confirmed(sender, reservation, **kwargs):
        NotificationService.dispatch_event(
            user=reservation.customer.user,
            event_type='RESERVATION_CONFIRMED',
            context={'reservation_number': reservation.reservation_number, 'date': str(reservation.reservation_date)},
            related_object=reservation
        )

    @receiver(donation_approved)
    def handle_donation_approved(sender, request, **kwargs):
        NotificationService.dispatch_event(
            user=request.ngo.user,
            event_type='DONATION_APPROVED',
            context={'organization': request.ngo.organization_name, 'quantity': request.approved_quantity},
            related_object=request
        )

    @receiver(listing_published)
    def handle_listing_published(sender, listing, **kwargs):
        # Notify subscribers or broad audience conceptually
        pass
        
setup_signal_listeners()
