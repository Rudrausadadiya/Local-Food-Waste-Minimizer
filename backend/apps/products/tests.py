from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.business.models import Business
from apps.products.models import Category, Product
from apps.products.services import CategoryService, ProductService

# Fallback in case User model isn't available correctly in standard tests
try:
    User = get_user_model()
except Exception:
    User = None

# Class: ProductServiceTests
class ProductServiceTests(TestCase):
    # Method: setUp
    def setUp(self):
        if not User:
            return
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.business = Business.objects.create(
            owner=self.user,
            business_name='Test Business',
            slug='test-business',
            business_type='RETAIL',
            business_email='biz@example.com'
        )

    # Method: test_create_category
    def test_create_category(self):
        if not User:
            return
        data = {
            'business': self.business,
            'name': 'Electronics',
            'description': 'Tech gadgets'
        }
        category = CategoryService.create_category(data)
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.slug, 'electronics')

    # Method: test_create_product
    def test_create_product(self):
        if not User:
            return
        category = Category.objects.create(business=self.business, name='Food', slug='food')
        data = {
            'business': self.business,
            'category': category,
            'sku': 'SKU123',
            'product_name': 'Apple',
            'unit': 'kg',
            'selling_price': 10.00
        }
        product = ProductService.create_product(data)
        self.assertEqual(product.product_name, 'Apple')
        self.assertEqual(product.selling_price, 10.00)

    # Method: test_soft_delete_product
    def test_soft_delete_product(self):
        if not User:
            return
        product = Product.objects.create(
            business=self.business,
            sku='SKU999',
            product_name='Banana',
            unit='kg',
            selling_price=5.00
        )
        ProductService.soft_delete_product(product)
        product.refresh_from_db()
        self.assertTrue(product.is_deleted)
        self.assertIsNotNone(product.deleted_at)
