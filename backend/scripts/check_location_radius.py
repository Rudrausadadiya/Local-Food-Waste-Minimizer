import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from common.utils import calculate_haversine_distance_km, validate_15km_radius
from django.core.exceptions import ValidationError

# Ahmedabad coordinates
user_ahmedabad_lat, user_ahmedabad_lon = 23.0225, 72.5714

# Nearby Ahmedabad store (~1.21 km away)
nearby_store_lat, nearby_store_lon = 23.0300, 72.5800

# California, USA store (~13,075 km away)
california_store_lat, california_store_lon = 37.7749, -122.4194

dist_nearby = calculate_haversine_distance_km(user_ahmedabad_lat, user_ahmedabad_lon, nearby_store_lat, nearby_store_lon)
print(f"Distance to nearby store: {dist_nearby:.2f} km")

dist_us = calculate_haversine_distance_km(user_ahmedabad_lat, user_ahmedabad_lon, california_store_lat, california_store_lon)
print(f"Distance to US California store: {dist_us:.2f} km")

try:
    validate_15km_radius(user_ahmedabad_lat, user_ahmedabad_lon, nearby_store_lat, nearby_store_lon)
    print("Nearby store validation: PASSED (Allowed)")
except ValidationError as e:
    print("Nearby store validation: FAILED -", str(e))

try:
    validate_15km_radius(user_ahmedabad_lat, user_ahmedabad_lon, california_store_lat, california_store_lon)
    print("US California store validation: UNEXPECTED PASS")
except ValidationError as e:
    print("US California store validation: BLOCKED (Success) ->", str(e))
