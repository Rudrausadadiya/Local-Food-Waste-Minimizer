from rest_framework import serializers
from .models import Business, Address, Branch, OperatingHours
from .validators import validate_gst, validate_phone, validate_currency, validate_timezone

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

class OperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatingHours
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

class BusinessSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    branches = BranchSerializer(many=True, read_only=True)
    operating_hours = OperatingHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner', 'is_verified', 'is_active', 'average_rating', 'total_reviews', 'business_status']

    def validate_gst_number(self, value):
        validate_gst(value)
        return value

    def validate_business_phone(self, value):
        validate_phone(value)
        return value

    def validate_currency(self, value):
        validate_currency(value)
        return value

    def validate_timezone(self, value):
        validate_timezone(value)
        return value
