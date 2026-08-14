import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.users.services import AuthService
from apps.users.choices import UserRole
from apps.business.models import Business

# 1. Register a Vendor
print("Registering vendor...")
vendor = AuthService.register(
    email='vendor_check@example.com',
    password='password123',
    first_name='V',
    last_name='T',
    role=UserRole.VENDOR,
    business_name='Vendor Check'
)

print("Vendor is_active:", vendor.is_active)
biz = vendor.businesses.first()
print("Business status:", biz.business_status)

# 2. Try to login immediately
try:
    user, tokens = AuthService.login('vendor_check@example.com', 'password123')
    print("Login BEFORE approval: SUCCESS")
except Exception as e:
    print("Login BEFORE approval: FAILED -", type(e).__name__, str(e))

# 3. Admin approves
print("Admin approving...")
biz.business_status = Business.BusinessStatus.APPROVED
biz.save()

# 4. Try to login after approval
try:
    user, tokens = AuthService.login('vendor_check@example.com', 'password123')
    print("Login AFTER approval: SUCCESS")
except Exception as e:
    print("Login AFTER approval: FAILED -", type(e).__name__, str(e))
