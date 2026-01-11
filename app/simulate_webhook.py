import os
import time
import json
import requests
import stripe
from django.conf import settings
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

def simulate_stripe_webhook(transaction_id):
    # 1. Configuration
    webhook_url = 'http://localhost:8000/api/webhook/stripe/'
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    print(f"--- Simulating Webhook for ID: {transaction_id} ---")
    print(f"Target URL: {webhook_url}")
    print(f"Signing Secret: {webhook_secret}")

    # 2. Build the Payload
    payload_data = {
        "id": "evt_test_simulation",
        "object": "event",
        "type": "payment_intent.succeeded",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": transaction_id,
                "object": "payment_intent",
                "amount": 100000, # 1000.00 currency units
                "currency": "usd",
                "status": "succeeded",
                "metadata": {
                    "provider": "Stripe"
                }
            }
        }
    }
    payload = json.dumps(payload_data)

    # 3. Generate Signature
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload}"
    # Signature generation needs correct compute_signature method or similar logic
    # stripe.WebhookSignature.generate_header might not be available in all versions
    # Use direct computation to be safe: HMAC-SHA256
    import hmac
    import hashlib
    
    mac = hmac.new(
        webhook_secret.encode('utf-8'),
        msg=f"{timestamp}.{payload}".encode('utf-8'),
        digestmod=hashlib.sha256
    )
    sig_hash = mac.hexdigest()
    
    signature = f"t={timestamp},v1={sig_hash}"

    # 4. Send Request
    headers = {
        'Content-Type': 'application/json',
        'Stripe-Signature': signature
    }

    try:
        response = requests.post(webhook_url, data=payload, headers=headers)
        print(f"\nResponse Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Webhook accepted successfully!")
        else:
            print("\n❌ Webhook failed.")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to localhost:8000. Is the server running?")

if __name__ == "__main__":
    # The ID extracted from your error message
    target_id = "pi_3SoUPH5ecmDryuK61bqnuc0v" 
    simulate_stripe_webhook(target_id)
