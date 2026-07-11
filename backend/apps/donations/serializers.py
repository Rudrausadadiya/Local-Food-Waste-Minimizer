from rest_framework import serializers
from .models import (
    NGO, NGODocument, DonationListing, DonationRequest,
    DonationPickup, DonationHistory, DonationImpact, PickupRoute
)
from .services import NGOService, DonationService

class NGODocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGODocument
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_at')

class NGOSerializer(serializers.ModelSerializer):
    documents = NGODocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = NGO
        fields = '__all__'
        read_only_fields = ('id', 'user', 'verification_status', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        return NGOService.register_ngo(user, validated_data)


class DonationListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationListing
        fields = '__all__'
        read_only_fields = ('id', 'donation_status', 'created_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return DonationService.create_listing(validated_data, user)


class DonationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRequest
        fields = '__all__'
        read_only_fields = ('id', 'request_status', 'approved_quantity', 'created_at', 'updated_at')


class DonationPickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationPickup
        fields = '__all__'
        read_only_fields = ('id', 'pickup_status', 'created_at', 'updated_at')


class DonationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationHistory
        fields = '__all__'
        
class DonationImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationImpact
        fields = '__all__'
        
class PickupRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupRoute
        fields = '__all__'
