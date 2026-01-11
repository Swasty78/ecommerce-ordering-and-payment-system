from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import Payment
from .serializers import PaymentSerializer
from .strategies import PaymentFactory
from core.constants import PaymentStatus, OrderStatus
import stripe
import logging

logger = logging.getLogger(__name__)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # We need to capture the client_secret from the strategy execution
        # but perform_create returns None. 
        # So we'll inline the logic here or modify perform_create to store it on the serializer instance temporarily.
        
        provider = serializer.validated_data.get('provider')
        order = serializer.validated_data.get('order')
        
        # Basic validation check before hitting external APIs
        if request.user != order.user:
             return Response({"detail": "You can only make payments for your own orders."}, status=status.HTTP_400_BAD_REQUEST)

        gateway = PaymentFactory.get_gateway(provider)
        try:
            result = gateway.process_payment(amount=order.total_amount)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the payment
        payment = serializer.save(
            transaction_id=result['transaction_id'],
            status=result['status']
        )
        
        # Prepare response
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        
        # Inject client_secret if available (standard for Stripe)
        if 'client_secret' in result:
            data['client_secret'] = result['client_secret']
            
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Override not needed as we overrode create()
        pass

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Simulate a payment confirmation (e.g. webhook or client-side success).
        In a real scenario, this might confirm via the gateway manually or be triggered by webhook.
        """
        payment = self.get_object()
        
        if payment.status == PaymentStatus.SUCCESS:
            return Response({'status': 'payment already completed'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Get Strategy
        gateway = PaymentFactory.get_gateway(payment.provider)

        # 2. Confirm Payment
        confirmation_status = gateway.confirm_payment(payment.transaction_id)
        
        if confirmation_status == PaymentStatus.SUCCESS:
            payment.status = PaymentStatus.SUCCESS
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = OrderStatus.PAID
            order.save()

            return Response({'status': 'payment completed', 'transaction_id': payment.transaction_id})
        
        return Response({'status': 'payment confirmation failed'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)

    return HttpResponse(status=200)

def handle_payment_success(payment_intent):
    transaction_id = payment_intent['id']
    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
        if payment.status != PaymentStatus.SUCCESS:
            payment.status = PaymentStatus.SUCCESS
            payment.save()
            
            order = payment.order
            order.status = OrderStatus.PAID
            order.save()
            logger.info(f"Payment {transaction_id} successfully processed via webhook.")
    except Payment.DoesNotExist:
        logger.warning(f"Payment with transaction_id {transaction_id} not found.")
