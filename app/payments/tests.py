from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Product, Category
from orders.models import Order
from .models import Payment
from core.constants import PaymentStatus, OrderStatus, PaymentProvider
from unittest.mock import patch

User = get_user_model()

class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.other_user = User.objects.create_user(email='other@example.com', password='password123')
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password123')
        
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Laptop', 
            slug='laptop', 
            price=1000.00, 
            stock=10, 
            category=self.category
        )
        
        self.order = Order.objects.create(user=self.user, total_amount=1000.00, shipping_address="123 Test St")
        self.other_order = Order.objects.create(user=self.other_user, total_amount=500.00, shipping_address="456 Other St")
        
        self.list_url = '/api/payments/'

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_stripe_strategy(self, mock_stripe_create):
        """Ensure Stripe strategy is used correctly."""
        mock_stripe_create.return_value = {
            'id': 'stripe_txn_mock',
            'client_secret': 'secret_mock',
            'status': 'pending'
        }
        
        data = {
            'order': self.order.id,
            'provider': PaymentProvider.STRIPE
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], PaymentStatus.PENDING)
        self.assertEqual(response.data['transaction_id'], 'stripe_txn_mock')
        self.assertEqual(float(response.data['amount']), 1000.00)

    def test_create_payment_bkash_strategy(self):
        """Ensure bKash strategy is used correctly."""
        data = {
            'order': self.order.id,
            'provider': PaymentProvider.BKASH
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], PaymentStatus.PENDING)
        self.assertTrue(response.data['transaction_id'].startswith('bkash_')) # Verified in logic
        self.assertEqual(float(response.data['amount']), 1000.00)

    def test_create_payment_invalid_order(self):
        """Ensure user cannot create payment for another user's order."""
        data = {
            'order': self.other_order.id,
            'provider': PaymentProvider.STRIPE
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('stripe.PaymentIntent.retrieve')
    def test_confirm_payment(self, mock_stripe_retrieve):
        """Ensure payment confirmation works via Strategy."""
        mock_stripe_retrieve.return_value = {'status': 'succeeded'}
        
        payment = Payment.objects.create(
            user=self.user, 
            order=self.order, 
            amount=1000.00, 
            provider=PaymentProvider.STRIPE,
            status=PaymentStatus.PENDING,
            transaction_id="stripe_txn_mock"
        )
        
        url = f"{self.list_url}{payment.id}/confirm/"
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, PaymentStatus.SUCCESS)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PAID)
