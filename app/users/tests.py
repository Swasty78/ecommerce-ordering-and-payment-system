from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'strongpassword123'
        }

    def test_registration_success(self):
        """
        Ensure we can register a new user.
        """
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        
        json_response = response.json()
        self.assertTrue(json_response['success'])

    def test_registration_duplicate_email(self):
        """
        Ensure we cannot register with the same email twice.
        """
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_fields(self):
        """
        Ensure registration fails if fields are missing.
        """
        data = {'email': 'incomplete@example.com'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """
        Ensure we can login and get tokens.
        """
        # Register first
        self.client.post(self.register_url, self.user_data)
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        json_response = response.json()
        self.assertIn('access', json_response['data'])
        self.assertIn('refresh', json_response['data'])
        self.assertTrue(json_response['success'])

    def test_login_invalid_credentials(self):
        """
        Ensure login fails with wrong password.
        """
        # Register first
        self.client.post(self.register_url, self.user_data)
        
        login_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
