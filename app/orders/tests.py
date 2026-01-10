from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from .models import Order

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        # Users
        self.user = User.objects.create_user(
            username='user@example.com',
            name='User', 
            email='user@example.com', 
            password='pass'
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            name='Other', 
            email='other@example.com', 
            password='pass'
        )
        self.admin = User.objects.create_user(
            username='admin@example.com',
            name='Admin', 
            email='admin@example.com', 
            password='pass',
            is_staff=True
        )

        # URLs
        self.order_list_url = reverse('order-list')

        # Sample Products
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Laptop', sku='LAP', price=1000.00, stock=10, 
            category=self.category, status=Product.Status.ACTIVE
        )
        self.product2 = Product.objects.create(
            name='Mouse', sku='MSE', price=50.00, stock=20, 
            category=self.category, status=Product.Status.ACTIVE
        )
        self.out_of_stock_product = Product.objects.create(
            name='Rare Item', sku='RARE', price=999.00, stock=0, 
            category=self.category, status=Product.Status.ACTIVE
        )

    def test_create_order_success(self):
        #Ensure user can create an order and stock is reduced.
        self.client.force_authenticate(user=self.user)
        data = {
            'shipping_address': '123 Test St, Test City',
            'order_items': [
                {'product_id': self.product1.id, 'quantity': 2},
                {'product_id': self.product2.id, 'quantity': 1}
            ]
        }
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check Order
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.shipping_address, '123 Test St, Test City')
        self.assertEqual(order.total_amount, 2050.00) # (1000*2) + (50*1)
        
        # Check Inventory Reduction
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 8) # 10 - 2
        self.assertEqual(self.product2.stock, 19) # 20 - 1

    def test_create_order_insufficient_stock(self):
        #Ensure order fails if stock is insufficient.
        self.client.force_authenticate(user=self.user)
        data = {
            'order_items': [
                {'product_id': self.product1.id, 'quantity': 11} # Stock is 10
            ]
        }
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_out_of_stock(self):
        #Ensure cannot order separate out of stock product.
        self.client.force_authenticate(user=self.user)
        data = {
            'order_items': [{'product_id': self.out_of_stock_product.id, 'quantity': 1}]
        }
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_permissions(self):
        #Ensure users only see their own orders.
        # Create order for user 1
        self.client.force_authenticate(user=self.user)
        data = {'order_items': [{'product_id': self.product1.id, 'quantity': 1}]}
        self.client.post(self.order_list_url, data, format='json')

        # Create order for user 2 (using a fresh client or just logic)
        Order.objects.create(user=self.other_user, total_amount=100)

        # User 1 should see 1 order
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(len(response.data), 1)

        # User 2 should see 1 order
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(len(response.data), 1)

    def test_admin_sees_all_orders(self):
        # Ensure admin sees orders from all users.
        Order.objects.create(user=self.user, total_amount=100)
        Order.objects.create(user=self.other_user, total_amount=200)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.order_list_url)
        self.assertEqual(len(response.data), 2)
