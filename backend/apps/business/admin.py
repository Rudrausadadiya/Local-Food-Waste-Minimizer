from django.contrib import admin
from .models import Business, Address, Branch, OperatingHours

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'owner', 'business_type', 'business_status', 'is_verified', 'is_active', 'created_at')
    list_filter = ('business_type', 'business_status', 'is_verified', 'is_active', 'is_deleted')
    search_fields = ('business_name', 'business_email', 'business_phone', 'slug')
    readonly_fields = ('id', 'slug', 'created_at', 'updated_at', 'deleted_at')
    
    def get_queryset(self, request):
        """
        Override to use the default manager to show deleted businesses in admin as well.
        """
        return self.model.objects.all()

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('business', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('business__business_name', 'city', 'state', 'postal_code')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'branch_code', 'business', 'is_main_branch', 'branch_status')
    list_filter = ('branch_status', 'is_main_branch')
    search_fields = ('branch_name', 'branch_code', 'business__business_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('business', 'get_weekday_display', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('weekday', 'is_closed')
    search_fields = ('business__business_name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
