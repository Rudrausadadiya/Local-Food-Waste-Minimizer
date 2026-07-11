from django.contrib import admin
from .models import Notification, NotificationPreference, NotificationTemplate, NotificationLog

class NotificationLogInline(admin.TabularInline):
    model = NotificationLog
    extra = 0
    readonly_fields = ('channel', 'provider', 'request_payload', 'response_payload', 'success', 'error_message', 'retry_count', 'delivered_at', 'opened_at', 'clicked_at', 'created_at')
    can_delete = False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'category', 'channel', 'priority', 'status', 'created_at')
    list_filter = ('status', 'channel', 'category', 'priority', 'is_archived')
    search_fields = ('title', 'recipient__email')
    inlines = [NotificationLogInline]
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled', 'digest_mode')
    list_filter = ('digest_mode',)
    search_fields = ('user__email',)

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'category', 'language', 'is_active')
    list_filter = ('category', 'language', 'is_active')
    search_fields = ('name', 'event_type')
