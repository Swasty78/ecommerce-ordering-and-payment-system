from abc import ABC, abstractmethod
from core.constants import PaymentStatus, PaymentProvider
from django.conf import settings
import stripe
import uuid

class PaymentGateway(ABC):
    """
    Abstract Base Class for Payment Strategies
    """
    @abstractmethod
    def process_payment(self, amount, currency='USD', **kwargs):
        """
        Initiate a payment transaction.
        Returns a dictionary with transaction_id and status.
        """
        pass

    @abstractmethod
    def confirm_payment(self, transaction_id, **kwargs):
        """
        Confirm a payment transaction.
        Returns boolean or status string.
        """
        pass

class StripePaymentGateway(PaymentGateway):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def process_payment(self, amount, currency='usd', **kwargs):
        try:
            # Stripe expects amount in cents
            amount_in_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=currency,
                metadata=kwargs.get('metadata', {}),
                payment_method_types=['card'], # Optional, defaults to configuration
            )
            
            return {
                'transaction_id': intent['id'],
                'client_secret': intent['client_secret'], # Frontend needs this to complete payment
                'status': PaymentStatus.PENDING,
                'metadata': {'provider': 'Stripe'}
            }
        except stripe.error.StripeError as e:
            # Handle Stripe API errors
            raise Exception(f"Stripe Error: {str(e)}")

    def confirm_payment(self, transaction_id, **kwargs):
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_id)
            if intent['status'] == 'succeeded':
                return PaymentStatus.SUCCESS
            elif intent['status'] == 'requires_payment_method':
                 return PaymentStatus.FAILED
            return PaymentStatus.PENDING
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe Error: {str(e)}")

class BkashPaymentGateway(PaymentGateway):
    def process_payment(self, amount, currency='BDT', **kwargs):
        # Mock bKash Logic
        transaction_id = f"bkash_txn_{uuid.uuid4().hex[:16]}"
        return {
            'transaction_id': transaction_id,
            'status': PaymentStatus.PENDING,
            'metadata': {'provider': 'bKash'}
        }

    def confirm_payment(self, transaction_id, **kwargs):
        # Mock bKash Confirmation
        return PaymentStatus.SUCCESS

class PaymentFactory:
    @staticmethod
    def get_gateway(provider):
        if provider == PaymentProvider.STRIPE:
            return StripePaymentGateway()
        elif provider == PaymentProvider.BKASH:
            return BkashPaymentGateway()
        else:
            raise ValueError(f"Invalid payment provider: {provider}")
