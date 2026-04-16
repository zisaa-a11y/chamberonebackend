from django.urls import path
from .views import (
    InvoiceListCreateView,
    InvoiceDetailView,
    InvoiceItemCreateView,
    InvoiceItemDeleteView,
    PaymentListCreateView,
    PaymentDetailView,
    PaymentStatusUpdateView,
    InvoicePaymentsView,
    PaymentCaseListView,
    PaymentSummaryView,
)
from .views.gateway_views import (
    BkashCreatePaymentView,
    BkashCallbackView,
    BkashQueryPaymentView,
    BkashRefundView,
    NagadCreatePaymentView,
    NagadCallbackView,
    NagadVerifyPaymentView,
    NagadRefundView,
)

app_name = 'payments'

urlpatterns = [
    # Invoices
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:invoice_id>/items/', InvoiceItemCreateView.as_view(), name='invoice_item_create'),
    path('invoices/items/<int:pk>/', InvoiceItemDeleteView.as_view(), name='invoice_item_delete'),
    path('invoices/<int:invoice_id>/payments/', InvoicePaymentsView.as_view(), name='invoice_payments'),
    path('cases/', PaymentCaseListView.as_view(), name='payment_cases'),
    
    # Payments
    path('', PaymentListCreateView.as_view(), name='payment_list'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('<int:pk>/status/', PaymentStatusUpdateView.as_view(), name='payment_status'),
    
    # Summary
    path('summary/', PaymentSummaryView.as_view(), name='payment_summary'),
    
    # bKash Payment Gateway
    path('bkash/create/', BkashCreatePaymentView.as_view(), name='bkash_create'),
    path('bkash/callback/', BkashCallbackView.as_view(), name='bkash_callback'),
    path('bkash/query/<str:payment_id>/', BkashQueryPaymentView.as_view(), name='bkash_query'),
    path('bkash/refund/', BkashRefundView.as_view(), name='bkash_refund'),
    
    # Nagad Payment Gateway
    path('nagad/create/', NagadCreatePaymentView.as_view(), name='nagad_create'),
    path('nagad/callback/', NagadCallbackView.as_view(), name='nagad_callback'),
    path('nagad/verify/<str:payment_ref_id>/', NagadVerifyPaymentView.as_view(), name='nagad_verify'),
    path('nagad/refund/', NagadRefundView.as_view(), name='nagad_refund'),
]
