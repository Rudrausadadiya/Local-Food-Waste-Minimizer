from django.contrib import admin
from .models import (
    NGO, NGODocument, DonationListing, DonationRequest,
    DonationPickup, DonationHistory, DonationImpact, PickupRoute
)

class NGODocumentInline(admin.TabularInline):
    model = NGODocument
    extra = 0

@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'registration_number', 'contact_person', 'verification_status', 'is_active')
    list_filter = ('verification_status', 'is_active')
    search_fields = ('organization_name', 'registration_number', 'email')
    inlines = [NGODocumentInline]

class DonationRequestInline(admin.TabularInline):
    model = DonationRequest
    extra = 0

class DonationHistoryInline(admin.TabularInline):
    model = DonationHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'remarks', 'changed_at')
    can_delete = False

@admin.register(DonationListing)
class DonationListingAdmin(admin.ModelAdmin):
    list_display = ('product', 'business', 'quantity', 'donation_status', 'priority', 'available_until')
    list_filter = ('donation_status', 'priority', 'visible_to_verified_ngos')
    search_fields = ('product__name', 'business__name')
    inlines = [DonationRequestInline, DonationHistoryInline]

class DonationImpactInline(admin.StackedInline):
    model = DonationImpact
    extra = 0
    readonly_fields = ('calculated_at',)

@admin.register(DonationPickup)
class DonationPickupAdmin(admin.ModelAdmin):
    list_display = ('donation_request', 'pickup_status', 'pickup_time', 'collected_by')
    list_filter = ('pickup_status',)
    inlines = [DonationImpactInline]

@admin.register(PickupRoute)
class PickupRouteAdmin(admin.ModelAdmin):
    list_display = ('ngo', 'route_date', 'driver_name')
    list_filter = ('route_date',)
