from django.contrib import admin
from .models import Table, Reservation, ReservationItem, ReservationTable, ReservationHistory

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'capacity', 'business', 'branch', 'is_active')
    list_filter = ('is_active', 'business', 'branch')
    search_fields = ('table_number',)

class ReservationItemInline(admin.TabularInline):
    model = ReservationItem
    extra = 0

class ReservationTableInline(admin.TabularInline):
    model = ReservationTable
    extra = 0

class ReservationHistoryInline(admin.TabularInline):
    model = ReservationHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'remarks', 'changed_at')
    can_delete = False

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'reservation_number', 'customer', 'reservation_date', 'reservation_time', 
        'party_size', 'reservation_status', 'reservation_type', 'business', 'branch'
    )
    list_filter = ('reservation_status', 'reservation_type', 'reservation_date', 'business', 'branch')
    search_fields = ('reservation_number', 'customer__first_name', 'customer__last_name', 'customer__phone')
    inlines = [ReservationTableInline, ReservationItemInline, ReservationHistoryInline]
    readonly_fields = ('id', 'created_at', 'updated_at')
