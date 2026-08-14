from django.contrib import admin
from .models import (
    NGO, NGODocument, DonationListing, DonationRequest,
    DonationPickup, DonationHistory, DonationImpact, PickupRoute
)

# Class: NGODocumentInline
class NGODocumentInline(admin.TabularInline):
    model = NGODocument
    extra = 0

@admin.register(NGO)
# Class: NGOAdmin
class NGOAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'registration_number', 'contact_person', 'verification_status', 'is_active')
    list_filter = ('verification_status', 'is_active')
    search_fields = ('organization_name', 'registration_number', 'email')
    inlines = [NGODocumentInline]

    # Method: save_model
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'verification_status' in form.changed_data:
            from apps.business.models import Business
            from apps.donations.models import NGOVerificationStatus
            if obj.verification_status == NGOVerificationStatus.VERIFIED:
                if obj.user:
                    obj.user.is_active = True
                    obj.user.save(update_fields=['is_active'])
                    Business.objects.filter(owner=obj.user).update(
                        business_status=Business.BusinessStatus.APPROVED,
                        is_active=True,
                        is_verified=True
                    )
            elif obj.verification_status == NGOVerificationStatus.REJECTED:
                if obj.user:
                    obj.user.is_active = False
                    obj.user.save(update_fields=['is_active'])
                    Business.objects.filter(owner=obj.user).update(
                        business_status=Business.BusinessStatus.SUSPENDED,
                        is_active=False,
                        is_verified=False
                    )

# Class: DonationRequestInline
class DonationRequestInline(admin.TabularInline):
    model = DonationRequest
    extra = 0

# Class: DonationHistoryInline
class DonationHistoryInline(admin.TabularInline):
    model = DonationHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'remarks', 'changed_at')
    can_delete = False

@admin.register(DonationListing)
# Class: DonationListingAdmin
class DonationListingAdmin(admin.ModelAdmin):
    list_display = ('product', 'business', 'quantity', 'donation_status', 'priority', 'available_until')
    list_filter = ('donation_status', 'priority', 'visible_to_verified_ngos')
    search_fields = ('product__name', 'business__name')
    inlines = [DonationRequestInline, DonationHistoryInline]

# Class: DonationImpactInline
class DonationImpactInline(admin.StackedInline):
    model = DonationImpact
    extra = 0
    readonly_fields = ('calculated_at',)

@admin.register(DonationPickup)
# Class: DonationPickupAdmin
class DonationPickupAdmin(admin.ModelAdmin):
    list_display = ('donation_request', 'pickup_status', 'pickup_time', 'collected_by')
    list_filter = ('pickup_status',)
    inlines = [DonationImpactInline]

@admin.register(PickupRoute)
# Class: PickupRouteAdmin
class PickupRouteAdmin(admin.ModelAdmin):
    list_display = ('ngo', 'route_date', 'driver_name')
    list_filter = ('route_date',)
