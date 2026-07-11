from django.dispatch import Signal

# Lifecycle Signals
listing_created = Signal()
listing_published = Signal()
listing_sold = Signal()
listing_expired = Signal()
listing_removed = Signal()

# Analytics and Engagement Signals
listing_viewed = Signal()
listing_added_to_wishlist = Signal()
listing_price_changed = Signal()
