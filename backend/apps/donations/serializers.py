from rest_framework import serializers
from .models import (
    NGO, NGODocument, DonationListing, DonationRequest,
    DonationPickup, DonationHistory, DonationImpact, PickupRoute
)
from .services import NGOService, DonationService

# Class: NGODocumentSerializer
class NGODocumentSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = NGODocument
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_at')

# Class: NGOSerializer
class NGOSerializer(serializers.ModelSerializer):
    documents = NGODocumentSerializer(many=True, read_only=True)
    
    # Class: Meta
    class Meta:
        model = NGO
        fields = '__all__'
        read_only_fields = ('id', 'user', 'verification_status', 'created_at', 'updated_at')

    # Method: create
    def create(self, validated_data):
        user = self.context['request'].user
        return NGOService.register_ngo(user, validated_data)


# Class: DonationListingSerializer
class DonationListingSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = DonationListing
        fields = '__all__'
        read_only_fields = ('id', 'donation_status', 'created_by', 'created_at', 'updated_at')

    # Method: create
    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return DonationService.create_listing(validated_data, user)


# Class: DonationRequestSerializer
class DonationRequestSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = DonationRequest
        fields = '__all__'
        read_only_fields = ('id', 'request_status', 'approved_quantity', 'created_at', 'updated_at')


# Class: DonationPickupSerializer
class DonationPickupSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = DonationPickup
        fields = '__all__'
        read_only_fields = ('id', 'pickup_status', 'created_at', 'updated_at')


# Class: DonationHistorySerializer
class DonationHistorySerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = DonationHistory
        fields = '__all__'
        
# Class: DonationImpactSerializer
class DonationImpactSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = DonationImpact
        fields = '__all__'
        
# Class: PickupRouteSerializer
class PickupRouteSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = PickupRoute
        fields = '__all__'
