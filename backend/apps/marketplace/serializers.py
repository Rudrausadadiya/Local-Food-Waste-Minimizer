from rest_framework import serializers
from .models import MarketplaceListing, MarketplaceOrder, Wishlist, MarketplaceReview
from .services import ListingService

class MarketplaceListingReadSerializer(serializers.ModelSerializer):
    # Assuming nested relations for read
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketplaceListing
        fields = '__all__'
        
    def get_discount_percentage(self, obj):
        if obj.original_price > 0:
            return round(((obj.original_price - obj.discounted_price) / obj.original_price) * 100, 2)
        return 0.00

class MarketplaceListingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceListing
        fields = [
            'business', 'branch', 'product', 'inventory_batch',
            'listing_title', 'description', 'original_price', 'discounted_price',
            'quantity_available', 'listing_type', 'pricing_strategy', 'expires_at',
            'image', 'is_featured', 'visible_to_ngos'
        ]

    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return ListingService.create_listing(validated_data, user)

    def update(self, instance, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return ListingService.update_listing(str(instance.id), validated_data, user)


class MarketplaceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceOrder
        fields = '__all__'
        read_only_fields = ('id', 'status', 'total_price', 'linked_order', 'created_at', 'updated_at')


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class MarketplaceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceReview
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
