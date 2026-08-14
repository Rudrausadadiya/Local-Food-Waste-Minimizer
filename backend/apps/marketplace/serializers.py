from rest_framework import serializers
from .models import MarketplaceListing, MarketplaceOrder, Wishlist, MarketplaceReview, ListingStatus
from .services import ListingService
from apps.business.models import Business
from apps.products.models import Product

# Class: MarketplaceListingReadSerializer
class MarketplaceListingReadSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.SerializerMethodField()
    
    # Class: Meta
    class Meta:
        model = MarketplaceListing
        fields = '__all__'
        
    # Method: get_discount_percentage
    def get_discount_percentage(self, obj):
        if obj.original_price > 0:
            return round(((obj.original_price - obj.discounted_price) / obj.original_price) * 100, 2)
        return 0.00

    # Method: to_representation
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        
        # Get address from branch or business default address
        branch_obj = instance.branch
        address_obj = None
        if branch_obj and branch_obj.address:
            address_obj = branch_obj.address
        elif instance.business and instance.business.addresses.exists():
            address_obj = instance.business.addresses.filter(is_default=True).first() or instance.business.addresses.first()

        address_data = None
        if address_obj:
            address_data = {
                'id': str(address_obj.id),
                'address_line_1': address_obj.address_line_1,
                'address_line_2': address_obj.address_line_2,
                'landmark': address_obj.landmark,
                'city': address_obj.city,
                'state': address_obj.state,
                'postal_code': address_obj.postal_code,
                'latitude': str(address_obj.latitude) if address_obj.latitude else None,
                'longitude': str(address_obj.longitude) if address_obj.longitude else None,
            }

        if instance.business:
            repr['business'] = {
                'id': str(instance.business.id),
                'business_name': instance.business.business_name,
                'business_type': instance.business.business_type,
                'business_email': instance.business.business_email,
                'business_phone': instance.business.business_phone,
                'is_verified': instance.business.is_verified,
                'average_rating': float(instance.business.average_rating) if instance.business.average_rating else 0.0,
                'address': address_data
            }

        if instance.branch:
            repr['branch'] = {
                'id': str(instance.branch.id),
                'branch_name': instance.branch.branch_name,
                'branch_code': instance.branch.branch_code,
                'address': address_data
            }
        elif address_data:
            repr['branch'] = {
                'address': address_data
            }

        if instance.product:
            image_url = None
            if instance.product.image and instance.product.image.name:
                try:
                    image_url = instance.product.image.url
                    request = self.context.get('request')
                    if request and not image_url.startswith('http'):
                        image_url = request.build_absolute_uri(image_url)
                except ValueError:
                    image_url = str(instance.product.image.name)

            repr['product'] = {
                'id': str(instance.product.id),
                'product_name': instance.product.product_name,
                'name': instance.product.product_name,
                'category': instance.product.category.name if instance.product.category else None,
                'image': image_url,
            }
            
            # Fallback for listing image if empty
            if not repr.get('image') and image_url:
                repr['image'] = image_url
            
        return repr

# Class: MarketplaceListingWriteSerializer
class MarketplaceListingWriteSerializer(serializers.ModelSerializer):
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)

    # Class: Meta
    class Meta:
        model = MarketplaceListing
        fields = [
            'business', 'branch', 'product', 'inventory_batch',
            'listing_title', 'description', 'original_price', 'discounted_price',
            'quantity_available', 'listing_type', 'pricing_strategy', 'expires_at',
            'image', 'is_featured', 'visible_to_ngos', 'listing_status'
        ]

    # Method: validate
    def validate(self, attrs):
        from django.utils import timezone
        from datetime import timedelta
        from apps.business.models import Business
        from apps.products.models import Product

        batch = attrs.get('inventory_batch')
        branch = attrs.get('branch')
        user = self.context['request'].user if 'request' in self.context else None

        if batch and not attrs.get('product'):
            attrs['product'] = batch.product

        if branch and not attrs.get('business'):
            attrs['business'] = branch.business

        if not attrs.get('business') and batch and hasattr(batch, 'branch') and batch.branch:
            attrs['business'] = batch.branch.business

        if not attrs.get('business') and user and hasattr(user, 'businesses'):
            biz = user.businesses.filter(is_deleted=False).first()
            if biz:
                attrs['business'] = biz

        if not attrs.get('business'):
            biz = Business.objects.first()
            if biz:
                attrs['business'] = biz

        if not attrs.get('product') and attrs.get('listing_title') and attrs.get('business'):
            prod, _ = Product.objects.get_or_create(
                business=attrs['business'],
                product_name=attrs['listing_title'],
                defaults={
                    'name': attrs['listing_title'],
                    'regular_price': attrs.get('original_price', 10.00),
                    'is_active': True
                }
            )
            attrs['product'] = prod

        # Ensure listing expiration is at least 7 days in the future so it never publishes as EXPIRED
        expires_at = attrs.get('expires_at')
        if not expires_at or expires_at <= timezone.now() + timedelta(hours=1):
            attrs['expires_at'] = timezone.now() + timedelta(days=7)

        if 'listing_status' not in attrs and not self.partial:
            attrs['listing_status'] = ListingStatus.PUBLISHED

        return attrs

    # Method: create
    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return ListingService.create_listing(validated_data, user)

    # Method: update
    def update(self, instance, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return ListingService.update_listing(str(instance.id), validated_data, user)


# Class: MarketplaceOrderSerializer
class MarketplaceOrderSerializer(serializers.ModelSerializer):
    claim_code = serializers.SerializerMethodField()

    # Class: Meta
    class Meta:
        model = MarketplaceOrder
        fields = '__all__'
        read_only_fields = ('id', 'status', 'total_price', 'linked_order', 'created_at', 'updated_at')

    # Method: get_claim_code
    def get_claim_code(self, obj):
        if obj.linked_order:
            return obj.linked_order.order_number
        return f"FW-{str(obj.id)[:6].upper()}"

    # Method: to_representation
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['listing'] = MarketplaceListingReadSerializer(instance.listing, context=self.context).data
        return repr


# Class: WishlistSerializer
class WishlistSerializer(serializers.ModelSerializer):
    listing_details = MarketplaceListingReadSerializer(source='listing', read_only=True)

    # Class: Meta
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'listing', 'listing_details', 'created_at']
        read_only_fields = ('id', 'user', 'created_at')


# Class: MarketplaceReviewSerializer
class MarketplaceReviewSerializer(serializers.ModelSerializer):
    # Class: Meta
    class Meta:
        model = MarketplaceReview
        fields = '__all__'
        read_only_fields = ('id', 'customer', 'created_at', 'updated_at')
