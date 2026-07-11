from django.contrib import admin
from .models import Customer, Order, OrderItem, Payment, Invoice, Sale, LoyaltyTransaction, Delivery

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'business', 'branch', 'customer', 'order_type', 'order_status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('order_status', 'payment_status', 'order_type', 'business', 'branch')
    search_fields = ('order_number', 'customer__first_name', 'customer__last_name', 'customer__phone')
    inlines = [OrderItemInline, PaymentInline, InvoiceInline]
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'business', 'loyalty_points', 'is_active', 'created_at')
    list_filter = ('is_active', 'business')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('order', 'business', 'branch', 'sale_date', 'revenue')
    list_filter = ('sale_date', 'business', 'branch')
    search_fields = ('order__order_number',)

@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'order', 'created_at')
    search_fields = ('customer__first_name', 'customer__phone')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'dispatched_at', 'delivered_at')
    list_filter = ('status',)
