from django.db import transaction
from django.utils.text import slugify
from .models import Category, Product, ProductImage
from .repositories import CategoryRepository, ProductRepository, ProductImageRepository
import uuid
import csv
from io import StringIO

class CategoryService:
    @staticmethod
    def create_category(data: dict) -> Category:
        slug = slugify(data.get('name', ''))
        if Category.objects.filter(slug=slug, business_id=data.get('business').id).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        data['slug'] = slug
        return CategoryRepository.create(data)

    @staticmethod
    def update_category(category: Category, data: dict) -> Category:
        if 'name' in data and data['name'] != category.name:
            slug = slugify(data['name'])
            if Category.objects.filter(slug=slug, business=category.business).exclude(id=category.id).exists():
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
            data['slug'] = slug
        return CategoryRepository.update(category, data)

    @staticmethod
    def soft_delete_category(category: Category) -> None:
        CategoryRepository.soft_delete(category)


class ProductService:
    @staticmethod
    def create_product(data: dict) -> Product:
        return ProductRepository.create(data)

    @staticmethod
    def update_product(product: Product, data: dict) -> Product:
        return ProductRepository.update(product, data)

    @staticmethod
    def soft_delete_product(product: Product) -> None:
        ProductRepository.soft_delete(product)


class ProductBulkService:
    @staticmethod
    @transaction.atomic
    def import_products_csv(business_id: str, file_obj) -> int:
        """
        Imports products from a CSV file.
        Format expected: sku, product_name, selling_price, unit, category_id
        """
        decoded_file = file_obj.read().decode('utf-8')
        io_string = StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        products_to_create = []
        for row in reader:
            category_id = row.get('category_id')
            if not category_id:
                category_id = None
                
            product = Product(
                business_id=business_id,
                sku=row.get('sku'),
                product_name=row.get('product_name'),
                selling_price=row.get('selling_price'),
                unit=row.get('unit'),
                category_id=category_id,
                barcode=row.get('barcode', ''),
                brand=row.get('brand', '')
            )
            products_to_create.append(product)
            
        ProductRepository.bulk_create(products_to_create)
        return len(products_to_create)


class ProductImageService:
    @staticmethod
    @transaction.atomic
    def upload_image(product: Product, data: dict) -> ProductImage:
        is_primary = data.get('is_primary', False)
        
        if is_primary:
            ProductImageRepository.unset_primary_for_product(product.id)
            
        # If this is the first image, make it primary automatically
        if not product.images.exists():
            data['is_primary'] = True
            
        data['product'] = product
        return ProductImageRepository.create(data)

    @staticmethod
    @transaction.atomic
    def set_primary_image(product_image: ProductImage) -> ProductImage:
        ProductImageRepository.unset_primary_for_product(product_image.product_id)
        return ProductImageRepository.update(product_image, {'is_primary': True})
        
    @staticmethod
    def delete_image(product_image: ProductImage) -> None:
        ProductImageRepository.delete(product_image)
