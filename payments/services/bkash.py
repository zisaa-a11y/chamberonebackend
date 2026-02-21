"""
bKash Payment Gateway Integration
Tokenized Checkout API v1.2.0-beta
"""

import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache


class BkashPaymentService:
    """
    bKash Tokenized Checkout Payment Service
    
    Flow:
    1. Grant Token - Get access token from bKash
    2. Create Payment - Initialize payment request
    3. Execute Payment - Complete payment after user authorization
    4. Query Payment - Check payment status
    5. Refund Payment - Refund a completed payment
    """
    
    def __init__(self):
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.base_url = settings.BKASH_BASE_URL
        
        # Token cache key
        self.token_cache_key = 'bkash_id_token'
    
    def _get_headers(self, include_auth=True):
        """Get headers for bKash API requests."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if include_auth:
            token = self._get_token()
            if token:
                headers['Authorization'] = token
                headers['X-APP-Key'] = self.app_key
        
        return headers
    
    def _get_token(self):
        """Get cached token or request new one."""
        token = cache.get(self.token_cache_key)
        
        if not token:
            token_response = self.grant_token()
            if token_response.get('statusCode') == '0000':
                token = token_response.get('id_token')
                # Cache for 55 minutes (token expires in 1 hour)
                cache.set(self.token_cache_key, token, 55 * 60)
        
        return token
    
    def grant_token(self):
        """
        Step 1: Get access token from bKash
        
        Returns:
            dict: Token response with id_token, token_type, expires_in, refresh_token
        """
        url = f"{self.base_url}/tokenized/checkout/token/grant"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'username': self.username,
            'password': self.password,
        }
        
        payload = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def refresh_token(self, refresh_token):
        """
        Refresh the access token using refresh token.
        
        Args:
            refresh_token: The refresh token from grant_token response
            
        Returns:
            dict: New token response
        """
        url = f"{self.base_url}/tokenized/checkout/token/refresh"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'username': self.username,
            'password': self.password,
        }
        
        payload = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'refresh_token': refresh_token,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()
            
            if result.get('statusCode') == '0000':
                # Update cached token
                cache.set(self.token_cache_key, result.get('id_token'), 55 * 60)
            
            return result
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def create_payment(self, amount, invoice_number, callback_url, payer_reference=None):
        """
        Step 2: Create a payment request
        
        Args:
            amount: Payment amount (minimum 1 BDT)
            invoice_number: Unique invoice/order number
            callback_url: URL to redirect after payment
            payer_reference: Optional payer reference (e.g., user ID)
            
        Returns:
            dict: Payment creation response with bkashURL for redirection
        """
        url = f"{self.base_url}/tokenized/checkout/create"
        
        headers = self._get_headers()
        
        payload = {
            'mode': '0011',  # Checkout URL mode
            'payerReference': payer_reference or invoice_number,
            'callbackURL': callback_url,
            'amount': str(amount),
            'currency': 'BDT',
            'intent': 'sale',
            'merchantInvoiceNumber': invoice_number,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def execute_payment(self, payment_id):
        """
        Step 3: Execute payment after user authorization
        
        Args:
            payment_id: The paymentID returned from create_payment
            
        Returns:
            dict: Payment execution response with transaction details
        """
        url = f"{self.base_url}/tokenized/checkout/execute"
        
        headers = self._get_headers()
        
        payload = {
            'paymentID': payment_id,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def query_payment(self, payment_id):
        """
        Query payment status
        
        Args:
            payment_id: The paymentID to query
            
        Returns:
            dict: Payment status details
        """
        url = f"{self.base_url}/tokenized/checkout/payment/status"
        
        headers = self._get_headers()
        
        payload = {
            'paymentID': payment_id,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def search_transaction(self, trx_id):
        """
        Search transaction by transaction ID
        
        Args:
            trx_id: The bKash transaction ID
            
        Returns:
            dict: Transaction details
        """
        url = f"{self.base_url}/tokenized/checkout/general/searchTransaction"
        
        headers = self._get_headers()
        
        payload = {
            'trxID': trx_id,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def refund_payment(self, payment_id, trx_id, amount, reason, sku=None):
        """
        Refund a completed payment
        
        Args:
            payment_id: The paymentID of the payment to refund
            trx_id: The transaction ID
            amount: Amount to refund
            reason: Reason for refund
            sku: Optional SKU reference
            
        Returns:
            dict: Refund response
        """
        url = f"{self.base_url}/tokenized/checkout/payment/refund"
        
        headers = self._get_headers()
        
        payload = {
            'paymentID': payment_id,
            'trxID': trx_id,
            'amount': str(amount),
            'reason': reason,
        }
        
        if sku:
            payload['sku'] = sku
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    def refund_status(self, payment_id, trx_id):
        """
        Check refund status
        
        Args:
            payment_id: The paymentID
            trx_id: The transaction ID
            
        Returns:
            dict: Refund status
        """
        url = f"{self.base_url}/tokenized/checkout/payment/refund"
        
        headers = self._get_headers()
        
        payload = {
            'paymentID': payment_id,
            'trxID': trx_id,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {
                'statusCode': 'error',
                'statusMessage': str(e)
            }
    
    @staticmethod
    def is_success(response):
        """Check if bKash response indicates success."""
        return response.get('statusCode') == '0000'
    
    @staticmethod
    def get_error_message(response):
        """Get error message from bKash response."""
        return response.get('statusMessage', 'Unknown error occurred')
