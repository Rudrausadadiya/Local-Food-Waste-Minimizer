from django.contrib import admin
from .models import Inventory, StockTransaction, InventoryBatch, Supplier, WasteRecord

@admin.register(Supplier)
# Class: SupplierAdmin
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'business', 'contact_person', 'phone', 'is_active')
    search_fields = ('supplier_name', 'business__business_name')
    list_filter = ('is_active', 'business')

@admin.register(Inventory)
# Class: InventoryAdmin
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'branch', 'business', 'current_stock', 'available_stock', 'reorder_level')
    search_fields = ('product__product_name', 'branch__branch_name')
    list_filter = ('business', 'branch', 'is_active')
    readonly_fields = ('current_stock', 'damaged_stock', 'expired_stock', 'reserved_stock')

@admin.register(StockTransaction)
# Class: StockTransactionAdmin
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'transaction_type', 'quantity', 'created_by', 'created_at')
    search_fields = ('inventory__product__product_name', 'reference_number')
    list_filter = ('transaction_type', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(InventoryBatch)
# Class: InventoryBatchAdmin
class InventoryBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'inventory', 'quantity', 'expiry_date', 'status')
    search_fields = ('batch_number', 'inventory__product__product_name')
    list_filter = ('status', 'expiry_date')

@admin.register(WasteRecord)
# Class: WasteRecordAdmin
class WasteRecordAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'quantity', 'waste_reason', 'recorded_by', 'created_at')
    search_fields = ('inventory__product__product_name',)
    list_filter = ('waste_reason', 'created_at')
    readonly_fields = ('created_at',)
