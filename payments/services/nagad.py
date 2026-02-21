"""
Nagad Payment Gateway Integration
"""

import requests
import json
import base64
import hashlib
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from django.conf import settings


class NagadPaymentService:
    """
    Nagad Payment Gateway Service
    
    Flow:
    1. Initialize - Get challenge from Nagad
    2. Complete Initialize - Send sensitive data encrypted
    3. Redirect to Nagad - User authorizes payment
    4. Callback - Receive payment confirmation
    5. Verify Payment - Verify payment status
    """
    
    def __init__(self):
        self.merchant_id = settings.NAGAD_MERCHANT_ID
        self.merchant_key = settings.NAGAD_MERCHANT_KEY
        self.base_url = settings.NAGAD_BASE_URL
        
        # Nagad public key for encryption (sandbox)
        self.nagad_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjBH1pFNSSRKPuMcNxmU5
jZ1x8K9LPFM4XSu11m7JCK7k5gm1weRkS1fkqXaCbMMSQ8d65k7TjqYhNxYr3Fiq
f4FP8bKLEk1H8wnFQJLjbxWR1JQXqCdE3y4eQATlAXPCqBK4EgMTdQHqbXcV7k9K
g9QJL4Hp1JPb8nvYxVsZuX+7+JjHQPZCqMNQRMPwGLpZ7m7nMqdD/FwBvh/8kNRu
kZ8l+o7yx+z5e7z4auZ7yxZ7T6QLxV/Aa1TlAzC/Sbl9B3k4Q5y8u9qTNpP5+fOo
ITQ8S21bm3asjEvQpMqQJ5v/sPVLedvBzHPwG2gV7L6qP/rqIvJkOw4x8q0q1vdd
LwIDAQAB
-----END PUBLIC KEY-----"""
        
        # Your merchant private key for signing
        self.merchant_private_key = settings.NAGAD_MERCHANT_KEY
    
    def _generate_timestamp(self):
        """Generate timestamp in Nagad format."""
        return datetime.now().strftime('%Y%m%d%H%M%S')
    
    def _encrypt_data(self, data):
        """Encrypt data using Nagad public key."""
        try:
            public_key = RSA.import_key(self.nagad_public_key)
            cipher = PKCS1_v1_5.new(public_key)
            
            data_bytes = json.dumps(data).encode('utf-8')
            encrypted = cipher.encrypt(data_bytes)
            
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def _sign_data(self, data):
        """Sign data using merchant private key."""
        try:
            if not self.merchant_private_key:
                return ""
            
            private_key = RSA.import_key(self.merchant_private_key)
            h = SHA256.new(data.encode('utf-8'))
            signature = pkcs1_15.new(private_key).sign(h)
            
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            # Return empty if signing fails (may not have private key)
            return ""
    
    def _get_headers(self):
        """Get headers for Nagad API requests."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-KM-Api-Version': 'v-0.2.0',
            'X-KM-IP-V4': '127.0.0.1',
            'X-KM-Client-Type': 'PC_WEB',
        }
    
    def initialize_payment(self, order_id, callback_url):
        """
        Step 1: Initialize payment and get challenge
        
        Args:
            order_id: Unique order/invoice ID
            callback_url: URL to redirect after payment
            
        Returns:
            dict: Initialize response with challenge
        """
        timestamp = self._generate_timestamp()
        
        url = f"{self.base_url}/check-out/initialize/{self.merchant_id}/{order_id}"
        
        # Sensitive data to encrypt
        sensitive_data = {
            'merchantId': self.merchant_id,
            'datetime': timestamp,
            'orderId': order_id,
            'challenge': self._generate_challenge(),
        }
        
        # Sign the sensitive data
        signature = self._sign_data(json.dumps(sensitive_data))
        
        payload = {
            'dateTime': timestamp,
            'sensitiveData': self._encrypt_data(sensitive_data),
            'signature': signature,
        }
        
        try:
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                json=payload,
                timeout=30
            )
            return response.json()
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def complete_payment(
        self, 
        order_id, 
        amount, 
        challenge, 
        payment_ref_id,
        callback_url,
        customer_name=None,
        customer_email=None,
        customer_phone=None
    ):
        """
        Step 2: Complete payment initialization with amount and customer details
        
        Args:
            order_id: Unique order/invoice ID
            amount: Payment amount
            challenge: Challenge from initialize response
            payment_ref_id: Payment reference ID from initialize
            callback_url: URL to redirect after payment
            customer_name: Optional customer name
            customer_email: Optional customer email
            customer_phone: Optional customer phone
            
        Returns:
            dict: Complete response with redirect URL
        """
        timestamp = self._generate_timestamp()
        
        url = f"{self.base_url}/check-out/complete/{payment_ref_id}"
        
        # Sensitive data
        sensitive_data = {
            'merchantId': self.merchant_id,
            'orderId': order_id,
            'currencyCode': '050',  # BDT
            'amount': str(amount),
            'challenge': challenge,
        }
        
        # Additional info
        additional_info = {}
        if customer_name:
            additional_info['customerName'] = customer_name
        if customer_email:
            additional_info['customerEmail'] = customer_email
        if customer_phone:
            additional_info['customerPhone'] = customer_phone
        
        # Sign the sensitive data
        signature = self._sign_data(json.dumps(sensitive_data))
        
        payload = {
            'dateTime': timestamp,
            'sensitiveData': self._encrypt_data(sensitive_data),
            'signature': signature,
            'merchantCallbackURL': callback_url,
        }
        
        if additional_info:
            payload['additionalMerchantInfo'] = additional_info
        
        try:
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                json=payload,
                timeout=30
            )
            return response.json()
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def verify_payment(self, payment_ref_id):
        """
        Verify payment status
        
        Args:
            payment_ref_id: The payment reference ID
            
        Returns:
            dict: Payment verification response
        """
        url = f"{self.base_url}/verify/payment/{payment_ref_id}"
        
        try:
            response = requests.get(
                url, 
                headers=self._get_headers(),
                timeout=30
            )
            return response.json()
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def refund_payment(self, payment_ref_id, amount, reference_no):
        """
        Refund a completed payment
        
        Args:
            payment_ref_id: The payment reference ID
            amount: Amount to refund
            reference_no: Reference number for refund
            
        Returns:
            dict: Refund response
        """
        url = f"{self.base_url}/api/dfs/refund-payment/refund"
        
        payload = {
            'merchantId': self.merchant_id,
            'originalPaymentReferenceId': payment_ref_id,
            'refundAmount': str(amount),
            'referenceNo': reference_no,
        }
        
        try:
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                json=payload,
                timeout=30
            )
            return response.json()
        except requests.RequestException as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _generate_challenge(self):
        """Generate a random challenge string."""
        import uuid
        return str(uuid.uuid4()).replace('-', '')[:20]
    
    @staticmethod
    def is_success(response):
        """Check if Nagad response indicates success."""
        return response.get('status') == 'Success'
    
    @staticmethod
    def get_error_message(response):
        """Get error message from Nagad response."""
        return response.get('message', 'Unknown error occurred')
