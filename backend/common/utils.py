import logging

# Function: get_logger
def get_logger(name):
    """
    Utility function to get a configured logger.
    """
    return logging.getLogger(name)

# Add other common utilities here as needed, such as:
# - Caching helpers
# - Common validators
# - Third-party service integrations (S3, Email, etc.)

import math
from django.core.exceptions import ValidationError

MAX_RESERVATION_RADIUS_KM = 15.0

# Function: calculate_haversine_distance_km
def calculate_haversine_distance_km(lat1, lon1, lat2, lon2) -> float:
    """
    Calculate the great-circle distance between two points on the Earth (in km)
    using the Haversine formula.
    """
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except (ValueError, TypeError):
        return 0.0

    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

# Function: get_branch_coordinates
def get_branch_coordinates(branch):
    """Extract latitude and longitude from a Branch or its Business Address."""
    if not branch:
        return None, None
    if getattr(branch, 'address', None):
        addr = branch.address
        if addr.latitude is not None and addr.longitude is not None:
            return float(addr.latitude), float(addr.longitude)
    if getattr(branch, 'business', None):
        addr = branch.business.addresses.filter(latitude__isnull=False, longitude__isnull=False).first()
        if addr:
            return float(addr.latitude), float(addr.longitude)
    return None, None

# Function: validate_15km_radius
def validate_15km_radius(user_lat, user_lon, target_lat, target_lon, entity_name="food item"):
    """
    Validates that the distance between user location and target location is within 15 km.
    Raises ValidationError if distance exceeds 15 km.
    """
    if user_lat is None or user_lon is None or target_lat is None or target_lon is None:
        return
        
    distance_km = calculate_haversine_distance_km(user_lat, user_lon, target_lat, target_lon)
    if distance_km > MAX_RESERVATION_RADIUS_KM:
        raise ValidationError(
            f"Cannot reserve {entity_name}. The location is {distance_km:.1f} km away from your location, "
            f"which exceeds the maximum allowed radius of {MAX_RESERVATION_RADIUS_KM} km."
        )

