from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with an admin user and sample products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # 1. Create Admin User
        admin_email = 'admin@example.com'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                username='admin',
                password='password123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin_email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {admin_email} already exists'))

        # 2. Create Categories
        categories = [
            {'name': 'Electronics', 'description': 'Gadgets and electronic devices'},
            {'name': 'Clothing', 'description': 'Apparel and fashion'},
            {'name': 'Books', 'description': 'Educational and entertainment books'},
        ]
        
        category_objs = {}
        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            category_objs[cat_data['name'].lower()] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat.name}"))

        # 3. Create Sample Products
        products = [
            {
                'name': 'Smartphone X',
                'sku': 'SMX-001',
                'category': category_objs['electronics'],
                'price': Decimal('999.00'),
                'stock': 50,
                'description': 'Latest smartphone with amazing features.'
            },
            {
                'name': 'Gaming Laptop',
                'sku': 'GL-500',
                'category': category_objs['electronics'],
                'price': Decimal('1500.00'),
                'stock': 20,
                'description': 'High performance laptop for gaming.'
            },
            {
                'name': 'Cool T-Shirt',
                'sku': 'TS-001',
                'category': category_objs['clothing'],
                'price': Decimal('25.00'),
                'stock': 100,
                'description': '100% Cotton comfortable t-shirt.'
            },
            {
                'name': 'Django for Beginners',
                'sku': 'BK-DJ-01',
                'category': category_objs['books'],
                'price': Decimal('39.99'),
                'stock': 500,
                'description': 'Learn web development with Python and Django.'
            }
        ]

        for prod_data in products:
            prod, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': prod_data['category'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'description': prod_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {prod.name}"))
            else:
                 self.stdout.write(self.style.WARNING(f"Product {prod.name} already exists"))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
