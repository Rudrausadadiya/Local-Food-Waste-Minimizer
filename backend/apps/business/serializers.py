from rest_framework import serializers
from .models import Business, Address, Branch, OperatingHours
from .validators import validate_gst, validate_phone, validate_currency, validate_timezone

# Class: AddressSerializer
class AddressSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

# Class: BranchSerializer
class BranchSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = Branch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

# Class: OperatingHoursSerializer
class OperatingHoursSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = OperatingHours
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

# Class: BusinessSerializer
class BusinessSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    branches = BranchSerializer(many=True, read_only=True)
    operating_hours = OperatingHoursSerializer(many=True, read_only=True)

    # Class: Meta
    class Meta:
        model = Business
        exclude = ['is_deleted', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner', 'is_verified', 'is_active', 'average_rating', 'total_reviews', 'business_status']

    # Method: validate_gst_number
    def validate_gst_number(self, value):
        validate_gst(value)
        return value

    # Method: validate_business_phone
    def validate_business_phone(self, value):
        validate_phone(value)
        return value

    # Method: validate_currency
    def validate_currency(self, value):
        validate_currency(value)
        return value

    # Method: validate_timezone
    def validate_timezone(self, value):
        validate_timezone(value)
        return value
