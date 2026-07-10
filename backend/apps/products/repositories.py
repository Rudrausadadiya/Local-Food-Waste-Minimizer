from typing import List, Optional
from django.db.models import QuerySet
from .models import Category, Product, ProductImage

class CategoryRepository:
    @staticmethod
    def create(data: dict) -> Category:
        return Category.objects.create(**data)

    @staticmethod
    def get_by_id(category_id: str) -> Optional[Category]:
        return Category.available_objects.filter(id=category_id).first()

    @staticmethod
    def get_by_business(business_id: str) -> QuerySet[Category]:
        return Category.available_objects.filter(business_id=business_id)

    @staticmethod
    def update(category: Category, data: dict) -> Category:
        for key, value in data.items():
            setattr(category, key, value)
        category.save()
        return category

    @staticmethod
    def soft_delete(category: Category) -> None:
        category.soft_delete()


class ProductRepository:
    @staticmethod
    def create(data: dict) -> Product:
        return Product.objects.create(**data)

    @staticmethod
    def get_by_id(product_id: str) -> Optional[Product]:
        return Product.available_objects.filter(id=product_id).first()

    @staticmethod
    def get_by_business(business_id: str) -> QuerySet[Product]:
        return Product.available_objects.filter(business_id=business_id)

    @staticmethod
    def update(product: Product, data: dict) -> Product:
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        return product

    @staticmethod
    def soft_delete(product: Product) -> None:
        product.soft_delete()

    @staticmethod
    def bulk_create(products: List[Product]) -> List[Product]:
        return Product.objects.bulk_create(products)


class ProductImageRepository:
    @staticmethod
    def create(data: dict) -> ProductImage:
        return ProductImage.objects.create(**data)

    @staticmethod
    def get_by_id(image_id: str) -> Optional[ProductImage]:
        return ProductImage.objects.filter(id=image_id).first()

    @staticmethod
    def get_by_product(product_id: str) -> QuerySet[ProductImage]:
        return ProductImage.objects.filter(product_id=product_id)

    @staticmethod
    def update(product_image: ProductImage, data: dict) -> ProductImage:
        for key, value in data.items():
            setattr(product_image, key, value)
        product_image.save()
        return product_image

    @staticmethod
    def delete(product_image: ProductImage) -> None:
        product_image.delete()

    @staticmethod
    def unset_primary_for_product(product_id: str) -> None:
        ProductImage.objects.filter(product_id=product_id, is_primary=True).update(is_primary=False)
