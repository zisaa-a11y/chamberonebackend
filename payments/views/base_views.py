from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum
import logging
from cases.models import Case
from cases.serializers import CaseListSerializer

from ..models import Invoice, InvoiceItem, Payment, Subscription
from ..serializers import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceListSerializer,
    InvoiceItemSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
)


logger = logging.getLogger(__name__)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access only to invoice/payment owner or admin."""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'client'):
            return obj.client == request.user or request.user.is_staff
        return request.user.is_staff


# Invoice Views
class InvoiceListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create invoices."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice_number', 'client__first_name', 'client__last_name']
    ordering_fields = ['issue_date', 'due_date', 'total_amount', 'status']
    ordering = ['-issue_date']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        return InvoiceListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.select_related('client', 'case')
        
        if user.is_staff:
            return queryset
        
        return queryset.filter(client=user)

    def create(self, request, *args, **kwargs):
        logger.info(
            'Invoice create requested: user=%s payload=%s',
            request.user.id,
            dict(request.data),
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        logger.info(
            'Invoice created: db_id=%s invoice_number=%s client_id=%s',
            invoice.id,
            invoice.invoice_number,
            invoice.client_id,
        )

        response_serializer = InvoiceSerializer(
            invoice,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for invoice detail."""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Invoice.objects.select_related('client', 'case').prefetch_related('items', 'payments')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InvoiceCreateSerializer
        return InvoiceSerializer


class InvoiceItemCreateView(generics.CreateAPIView):
    """API endpoint to add items to invoice."""
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        invoice_id = self.kwargs.get('invoice_id')
        serializer.save(invoice_id=invoice_id)
        
        # Update invoice subtotal
        invoice = Invoice.objects.get(pk=invoice_id)
        invoice.subtotal = invoice.items.aggregate(
            total=Sum('amount')
        )['total'] or 0
        invoice.save()


class InvoiceItemDeleteView(generics.DestroyAPIView):
    """API endpoint to delete invoice item."""
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InvoiceItem.objects.all()

    def perform_destroy(self, instance):
        invoice = instance.invoice
        instance.delete()
        
        # Update invoice subtotal
        invoice.subtotal = invoice.items.aggregate(
            total=Sum('amount')
        )['total'] or 0
        invoice.save()


# Payment Views
class PaymentListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create payments."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.select_related('client', 'invoice')
        
        if user.is_staff:
            return queryset
        
        return queryset.filter(client=user)

    def create(self, request, *args, **kwargs):
        logger.info(
            'Payment create requested: user=%s payload_keys=%s',
            request.user.id,
            sorted(list(request.data.keys())),
        )
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                'Payment create rejected: user=%s payload=%s errors=%s',
                request.user.id,
                dict(request.data),
                serializer.errors,
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        payment = serializer.save()
        logger.info(
            'Payment created: db_id=%s payment_id=%s invoice_id=%s client_id=%s',
            payment.id,
            payment.payment_id,
            payment.invoice_id,
            payment.client_id,
        )
        response_serializer = PaymentSerializer(payment, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PaymentDetailView(generics.RetrieveAPIView):
    """API endpoint for payment detail."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Payment.objects.select_related('client', 'invoice')


class PaymentStatusUpdateView(APIView):
    """API endpoint to update payment status (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Payment.Status.choices):
            return Response(
                {'error': 'Invalid status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = new_status
        
        # If completed, set payment date and update invoice
        if new_status == Payment.Status.COMPLETED:
            payment.payment_date = timezone.now()
            
            # Check if invoice is fully paid
            invoice = payment.invoice
            total_paid = invoice.payments.filter(
                status=Payment.Status.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if total_paid >= invoice.total_amount:
                invoice.status = Invoice.Status.PAID
                invoice.paid_date = timezone.now().date()
                invoice.save()
        
        payment.save()
        
        return Response(PaymentSerializer(payment, context={'request': request}).data)


class InvoicePaymentsView(generics.ListAPIView):
    """API endpoint to list payments for a specific invoice."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        invoice_id = self.kwargs.get('invoice_id')
        return Payment.objects.filter(
            invoice_id=invoice_id
        ).select_related('client')


class PaymentCaseListView(generics.ListAPIView):
    """Case list endpoint for payment/invoice forms."""
    serializer_class = CaseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'case_number', 'court_name']
    ordering_fields = ['created_at', 'next_hearing_date', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Case.objects.select_related('client', 'lawyer', 'lawyer__user').all()

        if user.is_staff:
            return queryset

        if hasattr(user, 'lawyer_profile'):
            return queryset.filter(lawyer=user.lawyer_profile)

        return queryset.filter(client=user)


class PaymentSummaryView(APIView):
    """API endpoint for payment summary/statistics."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.is_staff:
            payments = Payment.objects.all()
            invoices = Invoice.objects.all()
        else:
            payments = Payment.objects.filter(client=user)
            invoices = Invoice.objects.filter(client=user)
        
        total_paid = payments.filter(
            status=Payment.Status.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_pending = invoices.filter(
            status__in=[Invoice.Status.PENDING, Invoice.Status.OVERDUE]
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'total_paid': total_paid,
            'total_pending': total_pending,
            'pending_invoices_count': invoices.filter(
                status=Invoice.Status.PENDING
            ).count(),
            'overdue_invoices_count': invoices.filter(
                status=Invoice.Status.OVERDUE
            ).count(),
        })


class SubscriptionCreateView(generics.CreateAPIView):
    """API endpoint to create a subscription."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()), ['Invalid request data.'])
            if isinstance(first_error, list):
                message = str(first_error[0]) if first_error else 'Invalid request data.'
            else:
                message = str(first_error)
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

        subscription = serializer.save()

        # Keep payment_url in response even when redirect is not required.
        data = SubscriptionSerializer(subscription).data
        data.setdefault('payment_url', None)
        return Response(data, status=status.HTTP_201_CREATED)
