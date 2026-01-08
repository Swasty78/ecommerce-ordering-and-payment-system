from django.db import models

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PAID = 'paid', 'Paid'
    CANCELED = 'canceled', 'Canceled'

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'

class PaymentProvider(models.TextChoices):
    STRIPE = 'stripe', 'Stripe'
    BKASH = 'bkash', 'bKash'
