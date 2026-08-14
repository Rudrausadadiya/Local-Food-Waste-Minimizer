from django.contrib import admin
from .models import Business, Address, Branch, OperatingHours

@admin.register(Business)
# Class: BusinessAdmin
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'owner', 'business_type', 'business_status', 'is_verified', 'is_active', 'created_at')
    list_filter = ('business_type', 'business_status', 'is_verified', 'is_active', 'is_deleted')
    search_fields = ('business_name', 'business_email', 'business_phone', 'slug')
    readonly_fields = ('id', 'slug', 'created_at', 'updated_at', 'deleted_at')
    
    # Method: get_queryset
    def get_queryset(self, request):
        """
        Override to use the default manager to show deleted businesses in admin as well.
        """
        return self.model.objects.all()

    # Method: save_model
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'business_status' in form.changed_data:
            if obj.business_status == Business.BusinessStatus.APPROVED:
                obj.owner.is_active = True
                obj.owner.save(update_fields=['is_active'])
                if obj.owner.role == 'NGO' or obj.business_type == 'NGO':
                    from apps.donations.models import NGO, NGOVerificationStatus
                    NGO.objects.filter(user=obj.owner).update(
                        verification_status=NGOVerificationStatus.VERIFIED,
                        is_active=True
                    )
            elif obj.business_status in [Business.BusinessStatus.SUSPENDED, Business.BusinessStatus.REJECTED]:
                if obj.business_status == Business.BusinessStatus.SUSPENDED:
                    obj.owner.is_active = False
                    obj.owner.save(update_fields=['is_active'])
                if obj.owner.role == 'NGO' or obj.business_type == 'NGO':
                    from apps.donations.models import NGO, NGOVerificationStatus
                    ngo_status = NGOVerificationStatus.REJECTED if obj.business_status == Business.BusinessStatus.REJECTED else NGOVerificationStatus.PENDING
                    NGO.objects.filter(user=obj.owner).update(
                        verification_status=ngo_status,
                        is_active=False
                    )

@admin.register(Address)
# Class: AddressAdmin
class AddressAdmin(admin.ModelAdmin):
    list_display = ('business', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('business__business_name', 'city', 'state', 'postal_code')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Branch)
# Class: BranchAdmin
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'branch_code', 'business', 'is_main_branch', 'branch_status')
    list_filter = ('branch_status', 'is_main_branch')
    search_fields = ('branch_name', 'branch_code', 'business__business_name', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(OperatingHours)
# Class: OperatingHoursAdmin
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('business', 'get_weekday_display', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('weekday', 'is_closed')
    search_fields = ('business__business_name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
