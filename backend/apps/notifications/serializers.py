from rest_framework import serializers
from .models import Notification, NotificationPreference, NotificationTemplate, NotificationLog

# Class: NotificationSerializer
class NotificationSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'recipient', 'category', 'priority', 'status', 'group_key', 'is_archived', 'created_at', 'updated_at')

# Class: NotificationPreferenceSerializer
class NotificationPreferenceSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('id', 'user')

# Class: NotificationTemplateSerializer
class NotificationTemplateSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = NotificationTemplate
        fields = '__all__'

# Class: NotificationLogSerializer
class NotificationLogSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = NotificationLog
        fields = '__all__'
