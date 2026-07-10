from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import csv
from django.http import HttpResponse

from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer
from .services import CategoryService, ProductService, ProductBulkService, ProductImageService
from .permissions import IsBusinessOwnerOrAdmin
from .filters import ProductFilter

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD.
    """
    queryset = Category.available_objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsBusinessOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['business', 'is_active', 'parent_category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        business_id = self.request.query_params.get('business')
        if business_id:
            return self.queryset.filter(business_id=business_id)
        return self.queryset

    def perform_create(self, serializer):
        CategoryService.create_category(serializer.validated_data)

    def perform_update(self, serializer):
        CategoryService.update_category(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        CategoryService.soft_delete_category(instance)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD and Bulk operations.
    """
    queryset = Product.available_objects.all().prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [IsBusinessOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['sku', 'barcode', 'product_name', 'description']
    ordering_fields = ['product_name', 'selling_price', 'created_at']

    def perform_create(self, serializer):
        ProductService.create_product(serializer.validated_data)

    def perform_update(self, serializer):
        ProductService.update_product(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        ProductService.soft_delete_product(instance)

    from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'business_id': {'type': 'string', 'format': 'uuid'},
                    'file': {'type': 'string', 'format': 'binary'}
                },
                'required': ['business_id', 'file']
            }
        },
        responses={201: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        description="Bulk import products from CSV."
    )
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        business_id = request.data.get('business_id')
        file_obj = request.FILES.get('file')
        if not business_id or not file_obj:
            return Response({'error': 'business_id and file are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            count = ProductBulkService.import_products_csv(business_id, file_obj)
            return Response({'message': f'Successfully imported {count} products.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='business_id', description='Business ID', required=True, type=OpenApiTypes.UUID)
        ],
        responses={(200, 'text/csv'): OpenApiTypes.BINARY},
        description="Bulk export products as CSV."
    )
    @action(detail=False, methods=['get'])
    def bulk_export(self, request):
        business_id = request.query_params.get('business_id')
        if not business_id:
            return Response({'error': 'business_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        products = Product.available_objects.filter(business_id=business_id)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['sku', 'barcode', 'product_name', 'selling_price', 'unit', 'brand'])
        for product in products:
            writer.writerow([product.sku, product.barcode, product.product_name, product.selling_price, product.unit, product.brand])
            
        return response


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product Images.
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsBusinessOwnerOrAdmin]

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = Product.available_objects.filter(id=product_id).first()
        from rest_framework import serializers
        if not product:
            raise serializers.ValidationError({'product': 'Invalid product ID'})
        ProductImageService.upload_image(product, serializer.validated_data)

    def perform_destroy(self, instance):
        ProductImageService.delete_image(instance)

    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        instance = self.get_object()
        ProductImageService.set_primary_image(instance)
        return Response({'message': 'Image set as primary successfully.'})
