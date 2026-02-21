"""
Payment Gateway Views for bKash and Nagad
"""

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum

from ..models import Invoice, Payment
from ..services.bkash import BkashPaymentService
from ..services.nagad import NagadPaymentService


# ==================== bKash Views ====================

class BkashCreatePaymentView(APIView):
    """
    Create bKash payment for an invoice
    
    POST /api/payments/bkash/create/
    {
        "invoice_id": 1
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        invoice_id = request.data.get('invoice_id')
        
        if not invoice_id:
            return Response(
                {'error': 'Invoice ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(pk=invoice_id, client=request.user)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invoice.status == Invoice.Status.PAID:
            return Response(
                {'error': 'Invoice is already paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate remaining amount
        paid_amount = invoice.payments.filter(
            status=Payment.Status.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        remaining_amount = invoice.total_amount - paid_amount
        
        if remaining_amount <= 0:
            return Response(
                {'error': 'No remaining amount to pay.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get callback URL
        callback_url = request.build_absolute_uri('/api/payments/bkash/callback/')
        
        # Create bKash payment
        bkash = BkashPaymentService()
        result = bkash.create_payment(
            amount=float(remaining_amount),
            invoice_number=invoice.invoice_number,
            callback_url=callback_url,
            payer_reference=str(request.user.id)
        )
        
        if bkash.is_success(result):
            # Create payment record
            payment = Payment.objects.create(
                invoice=invoice,
                client=request.user,
                amount=remaining_amount,
                payment_method='bkash',
                status=Payment.Status.PENDING,
                transaction_id=result.get('paymentID'),
                gateway_response=result
            )
            
            return Response({
                'success': True,
                'payment_id': payment.id,
                'bkash_url': result.get('bkashURL'),
                'message': 'Redirect to bKash to complete payment.'
            })
        else:
            return Response({
                'success': False,
                'error': bkash.get_error_message(result)
            }, status=status.HTTP_400_BAD_REQUEST)


class BkashCallbackView(APIView):
    """
    bKash payment callback
    
    GET /api/payments/bkash/callback/?paymentID=xxx&status=success
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        payment_id = request.GET.get('paymentID')
        payment_status = request.GET.get('status')
        
        if not payment_id:
            return Response(
                {'error': 'Payment ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find payment record
        try:
            payment = Payment.objects.get(transaction_id=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if payment_status == 'success':
            # Execute payment
            bkash = BkashPaymentService()
            result = bkash.execute_payment(payment_id)
            
            if bkash.is_success(result):
                payment.status = Payment.Status.COMPLETED
                payment.transaction_id = result.get('trxID', payment_id)
                payment.payment_date = timezone.now()
                payment.gateway_response = result
                payment.save()
                
                # Update invoice status if fully paid
                invoice = payment.invoice
                total_paid = invoice.payments.filter(
                    status=Payment.Status.COMPLETED
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                if total_paid >= invoice.total_amount:
                    invoice.status = Invoice.Status.PAID
                    invoice.paid_date = timezone.now().date()
                    invoice.save()
                
                # Redirect to success page
                frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'
                return redirect(f"{frontend_url}/payment/success?payment_id={payment.id}")
            else:
                payment.status = Payment.Status.FAILED
                payment.gateway_response = result
                payment.save()
                
                frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'
                return redirect(f"{frontend_url}/payment/failed?error={bkash.get_error_message(result)}")
        
        elif payment_status == 'cancel':
            payment.status = Payment.Status.CANCELLED
            payment.save()
            
            frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'
            return redirect(f"{frontend_url}/payment/cancelled")
        
        else:
            payment.status = Payment.Status.FAILED
            payment.save()
            
            frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'
            return redirect(f"{frontend_url}/payment/failed")


class BkashQueryPaymentView(APIView):
    """
    Query bKash payment status
    
    GET /api/payments/bkash/query/<payment_id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_id):
        bkash = BkashPaymentService()
        result = bkash.query_payment(payment_id)
        
        return Response(result)


class BkashRefundView(APIView):
    """
    Refund bKash payment
    
    POST /api/payments/bkash/refund/
    {
        "payment_id": 1,
        "amount": 100,
        "reason": "Customer requested refund"
    }
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        payment_id = request.data.get('payment_id')
        amount = request.data.get('amount')
        reason = request.data.get('reason', 'Refund requested')
        
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if payment.status != Payment.Status.COMPLETED:
            return Response(
                {'error': 'Only completed payments can be refunded.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bkash = BkashPaymentService()
        result = bkash.refund_payment(
            payment_id=payment.gateway_response.get('paymentID'),
            trx_id=payment.transaction_id,
            amount=amount or float(payment.amount),
            reason=reason
        )
        
        if bkash.is_success(result):
            payment.status = Payment.Status.REFUNDED
            payment.gateway_response = result
            payment.save()
            
            return Response({
                'success': True,
                'message': 'Payment refunded successfully.',
                'refund_details': result
            })
        else:
            return Response({
                'success': False,
                'error': bkash.get_error_message(result)
            }, status=status.HTTP_400_BAD_REQUEST)


# ==================== Nagad Views ====================

class NagadCreatePaymentView(APIView):
    """
    Create Nagad payment for an invoice
    
    POST /api/payments/nagad/create/
    {
        "invoice_id": 1
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        invoice_id = request.data.get('invoice_id')
        
        if not invoice_id:
            return Response(
                {'error': 'Invoice ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(pk=invoice_id, client=request.user)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invoice.status == Invoice.Status.PAID:
            return Response(
                {'error': 'Invoice is already paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate remaining amount
        from django.db.models import Sum
        paid_amount = invoice.payments.filter(
            status=Payment.Status.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        remaining_amount = invoice.total_amount - paid_amount
        
        if remaining_amount <= 0:
            return Response(
                {'error': 'No remaining amount to pay.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get callback URL
        callback_url = request.build_absolute_uri('/api/payments/nagad/callback/')
        
        # Initialize Nagad payment
        nagad = NagadPaymentService()
        init_result = nagad.initialize_payment(
            order_id=invoice.invoice_number,
            callback_url=callback_url
        )
        
        if nagad.is_success(init_result):
            # Complete payment initialization
            complete_result = nagad.complete_payment(
                order_id=invoice.invoice_number,
                amount=float(remaining_amount),
                challenge=init_result.get('challenge'),
                payment_ref_id=init_result.get('paymentReferenceId'),
                callback_url=callback_url,
                customer_name=request.user.full_name,
                customer_email=request.user.email,
                customer_phone=request.user.phone
            )
            
            if nagad.is_success(complete_result):
                # Create payment record
                payment = Payment.objects.create(
                    invoice=invoice,
                    client=request.user,
                    amount=remaining_amount,
                    payment_method='nagad',
                    status=Payment.Status.PENDING,
                    transaction_id=complete_result.get('paymentReferenceId'),
                    gateway_response=complete_result
                )
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'nagad_url': complete_result.get('callBackUrl'),
                    'message': 'Redirect to Nagad to complete payment.'
                })
            else:
                return Response({
                    'success': False,
                    'error': nagad.get_error_message(complete_result)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'error': nagad.get_error_message(init_result)
            }, status=status.HTTP_400_BAD_REQUEST)


class NagadCallbackView(APIView):
    """
    Nagad payment callback
    
    GET /api/payments/nagad/callback/?payment_ref_id=xxx&status=Success
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        payment_ref_id = request.GET.get('payment_ref_id')
        payment_status = request.GET.get('status')
        
        if not payment_ref_id:
            # Try POST data
            payment_ref_id = request.data.get('payment_ref_id')
            payment_status = request.data.get('status')
        
        if not payment_ref_id:
            return Response(
                {'error': 'Payment reference ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find payment record
        try:
            payment = Payment.objects.get(transaction_id=payment_ref_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify payment
        nagad = NagadPaymentService()
        result = nagad.verify_payment(payment_ref_id)
        
        frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'
        
        if nagad.is_success(result):
            payment.status = Payment.Status.COMPLETED
            payment.transaction_id = result.get('issuerPaymentRefNo', payment_ref_id)
            payment.payment_date = timezone.now()
            payment.gateway_response = result
            payment.save()
            
            # Update invoice status if fully paid
            invoice = payment.invoice
            from django.db.models import Sum
            total_paid = invoice.payments.filter(
                status=Payment.Status.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if total_paid >= invoice.total_amount:
                invoice.status = Invoice.Status.PAID
                invoice.paid_date = timezone.now().date()
                invoice.save()
            
            return redirect(f"{frontend_url}/payment/success?payment_id={payment.id}")
        else:
            payment.status = Payment.Status.FAILED
            payment.gateway_response = result
            payment.save()
            
            return redirect(f"{frontend_url}/payment/failed?error={nagad.get_error_message(result)}")
    
    def post(self, request):
        """Handle POST callback from Nagad."""
        return self.get(request)


class NagadVerifyPaymentView(APIView):
    """
    Verify Nagad payment status
    
    GET /api/payments/nagad/verify/<payment_ref_id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_ref_id):
        nagad = NagadPaymentService()
        result = nagad.verify_payment(payment_ref_id)
        
        return Response(result)


class NagadRefundView(APIView):
    """
    Refund Nagad payment
    
    POST /api/payments/nagad/refund/
    {
        "payment_id": 1,
        "amount": 100,
        "reference_no": "REF123"
    }
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        payment_id = request.data.get('payment_id')
        amount = request.data.get('amount')
        reference_no = request.data.get('reference_no')
        
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if payment.status != Payment.Status.COMPLETED:
            return Response(
                {'error': 'Only completed payments can be refunded.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reference_no:
            reference_no = f"REF-{payment.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        nagad = NagadPaymentService()
        result = nagad.refund_payment(
            payment_ref_id=payment.transaction_id,
            amount=amount or float(payment.amount),
            reference_no=reference_no
        )
        
        if nagad.is_success(result):
            payment.status = Payment.Status.REFUNDED
            payment.gateway_response = result
            payment.save()
            
            return Response({
                'success': True,
                'message': 'Payment refunded successfully.',
                'refund_details': result
            })
        else:
            return Response({
                'success': False,
                'error': nagad.get_error_message(result)
            }, status=status.HTTP_400_BAD_REQUEST)
