from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Category, Product

User = get_user_model()

class ProductTests(APITestCase):
    def setUp(self):
        # Users
        self.admin = User.objects.create_user(
            username='admin@example.com', 
            name='Admin', 
            email='admin@example.com', 
            password='pass', 
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='user@example.com',
            name='User', 
            email='user@example.com', 
            password='pass'
        )
        
        # URLs
        # DRF DefaultRouter creates names based on the basename (defaulting to queryset model name lowercased)
        self.category_list_url = reverse('category-list') 
        self.product_list_url = reverse('product-list')

        # Sample Data
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop', 
            sku='LAP-001', 
            price=1000.00, 
            category=self.category,
            status=Product.Status.ACTIVE
        )

    def test_list_products_public(self):
        
        #Ensure public users can list active products.
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Laptop')

    def test_create_product_admin(self):
        
        # Ensure admins can create products.
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Phone',
            'sku': 'PHN-001',
            'price': 500.00,
            'category_id': self.category.id,
            'status': 'active'
        }
        response = self.client.post(self.product_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.get(sku='PHN-001').name, 'Phone')

    def test_create_product_forbidden_for_user(self):
        # Ensure regular users cannot create products.
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Hacker Product',
            'sku': 'HACK-001', 
            'price': 10.00,
            'category_id': self.category.id
        }
        response = self.client.post(self.product_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_admin(self):
        
        #Ensure admins can update product details. 
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-detail', args=[self.product.id])
        data = {'price': 1200.00}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 1200.00)

    def test_visibility_inactive_products(self):
        
        #Ensure inactive products are hidden from public but visible to admins.
        Product.objects.create(
            name='Old Phone', 
            sku='OLD-001', 
            price=10.00, 
            status=Product.Status.INACTIVE
        )
        
        # 1. Unauthenticated User -> Should see only ACTIVE (1)
        response = self.client.get(self.product_list_url)
        self.assertEqual(len(response.data), 1)

        # 2. Regular User -> Should see only ACTIVE (1)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.product_list_url)
        self.assertEqual(len(response.data), 1)

        # 3. Admin User -> Should see ALL (2)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.product_list_url)
        self.assertEqual(len(response.data), 2)

    def test_create_category_admin(self):
        
        #Ensure admins can create categories.
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Home & Garden', 'description': 'Stuff for home'}
        response = self.client.post(self.category_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_filter_products_by_category(self):
        
        #Ensure filtering by category works.
        new_cat = Category.objects.create(name='Books')
        Product.objects.create(name='Book 1', sku='BK-1', price=5, category=new_cat)
        
        # Filter for Electronics (existing product)
        response = self.client.get(self.product_list_url, {'category_id': self.category.id})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Laptop')

        # Filter for Books
        response = self.client.get(self.product_list_url, {'category_id': new_cat.id})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Book 1')
