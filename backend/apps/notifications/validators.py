from django.utils import timezone

# Function: validate_quiet_hours
def validate_quiet_hours(pref, scheduled_at=None):
    """
    Returns True if the current or scheduled time is during quiet hours.
    """
    if not pref.quiet_hours_start or not pref.quiet_hours_end:
        return False
        
    check_time = scheduled_at if scheduled_at else timezone.now()
    check_time = timezone.localtime(check_time).time()
    
    start = pref.quiet_hours_start
    end = pref.quiet_hours_end
    
    if start < end:
        return start <= check_time <= end
    else: # Crosses midnight
        return check_time >= start or check_time <= end

# Function: is_channel_enabled
def is_channel_enabled(pref, channel: str, event_type: str = None) -> bool:
    """
    Validates if the user allows the channel globally or per-event.
    """
    global_enabled = getattr(pref, f"{channel.lower()}_enabled", True)
    
    if not global_enabled:
        return False
        
    if event_type and pref.per_event_preferences:
        event_prefs = pref.per_event_preferences.get(event_type, {})
        # If it's explicitly set to False, deny it. If True or unset, allow it.
        if event_prefs.get(channel.lower()) is False:
            return False
            
    return True
