from rest_framework import serializers
import logging
from .models import Invoice, InvoiceItem, Payment, Subscription
from accounts.serializers import UserSerializer
from cases.serializers import CaseListSerializer
from cases.models import Case


logger = logging.getLogger(__name__)


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model."""
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'invoice', 'description', 'quantity', 'unit_price', 'amount']
        read_only_fields = ['id', 'amount']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    client = UserSerializer(read_only=True)
    client_name = serializers.ReadOnlyField()
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    case_id = serializers.IntegerField(source='case.id', read_only=True)
    case_number = serializers.CharField(source='case.case_number', read_only=True)
    case_title = serializers.CharField(source='case.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'invoice', 'invoice_number', 'client', 'client_name',
            'case_id', 'case_number', 'case_title',
            'amount', 'payment_method', 'method_display',
            'status', 'status_display', 'transaction_id',
            'payment_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Full serializer for Invoice model."""
    client = UserSerializer(read_only=True)
    case_details = CaseListSerializer(source='case', read_only=True)
    client_name = serializers.ReadOnlyField()
    case_title = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client', 'client_name',
            'case', 'case_details', 'case_title',
            'description', 'subtotal', 'tax_amount', 'total_amount',
            'status', 'status_display',
            'issue_date', 'due_date', 'paid_date',
            'notes', 'items', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'total_amount',
            'created_at', 'updated_at'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices."""
    items = InvoiceItemSerializer(many=True, required=False)
    client_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    case_title = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'client', 'client_name', 'case', 'case_title', 'description',
            'subtotal', 'tax_amount',
            'status', 'issue_date', 'due_date', 'notes', 'items'
        ]
        extra_kwargs = {
            'client': {'required': False},
        }

    def create(self, validated_data):
        validated_data.pop('client_name', None)
        validated_data.pop('case_title', None)
        items_data = validated_data.pop('items', [])
        # Auto-assign client from request user if not provided
        if 'client' not in validated_data or validated_data['client'] is None:
            validated_data['client'] = self.context['request'].user
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Recalculate subtotal from items
        if items_data:
            invoice.subtotal = sum(
                item.amount for item in invoice.items.all()
            )
            invoice.save()
        
        return invoice

    def to_internal_value(self, data):
        mutable = data.copy()
        for key in ('issue_date', 'due_date'):
            value = mutable.get(key)
            if isinstance(value, str) and 'T' in value:
                mutable[key] = value.split('T', 1)[0]

        return super().to_internal_value(mutable)


class InvoiceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing invoices."""
    client_name = serializers.ReadOnlyField()
    case_title = serializers.ReadOnlyField()
    case_number = serializers.CharField(source='case.case_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'case', 'case_title', 'case_number',
            'total_amount', 'status', 'status_display',
            'issue_date', 'due_date'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    invoice = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.none(),
        required=False,
        allow_null=True,
        error_messages={
            'required': 'Invoice ID is required when case_id is not provided.',
            'does_not_exist': 'Invoice not found. Create invoice in backend first, then retry payment.',
            'incorrect_type': 'Invoice ID must be a valid integer.',
            'null': 'Invoice ID cannot be null.',
        },
    )
    case_id = serializers.PrimaryKeyRelatedField(
        queryset=Case.objects.none(),
        source='case',
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Case ID is required.',
            'does_not_exist': 'Case not found.',
            'incorrect_type': 'Case ID must be a valid integer.',
            'null': 'Case ID cannot be null.',
        },
    )
    payment_method = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = Payment
        fields = ['invoice', 'case_id', 'amount', 'payment_method', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user is None or not getattr(user, 'is_authenticated', False):
            return

        if user.is_staff:
            self.fields['invoice'].queryset = Invoice.objects.all()
            self.fields['case_id'].queryset = Case.objects.all()
        else:
            self.fields['invoice'].queryset = Invoice.objects.filter(client=user)
            self.fields['case_id'].queryset = Case.objects.filter(client=user)

    def validate(self, attrs):
        invoice = attrs.get('invoice')
        case = attrs.get('case')

        if case is None:
            raise serializers.ValidationError({'case_id': 'Case ID is required.'})

        if invoice is not None and invoice.case_id and invoice.case_id != case.id:
            raise serializers.ValidationError({'invoice': 'Invoice does not belong to selected case.'})

        return attrs

    def validate_invoice(self, invoice):
        logger.info(
            'Payment serializer invoice validated: invoice_id=%s client_id=%s',
            invoice.id,
            invoice.client_id,
        )
        return invoice

    def validate_payment_method(self, value):
        alias_map = {
            'credit_card': Payment.PaymentMethod.CARD,
            'debit_card': Payment.PaymentMethod.CARD,
            'netbanking': Payment.PaymentMethod.BANK_TRANSFER,
            'bank': Payment.PaymentMethod.BANK_TRANSFER,
            'wallet': Payment.PaymentMethod.MOBILE,
            'mobile_banking': Payment.PaymentMethod.MOBILE,
            'ssl': Payment.PaymentMethod.SSLCOMMERZ,
            'ssl_commerz': Payment.PaymentMethod.SSLCOMMERZ,
            'sslc': Payment.PaymentMethod.SSLCOMMERZ,
            'upi': Payment.PaymentMethod.OTHER,
        }
        normalized = (value or '').strip().lower()
        if not normalized:
            return Payment.PaymentMethod.CARD

        resolved = alias_map.get(normalized, normalized)
        valid_methods = dict(Payment.PaymentMethod.choices)
        if resolved not in valid_methods:
            raise serializers.ValidationError('Unsupported payment method.')
        return resolved

    def create(self, validated_data):
        # Keep payment ownership aligned with the selected case owner.
        validated_data['client'] = validated_data['case'].client
        return super().create(validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'status', 'payment_url',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'payment_url', 'created_at', 'updated_at']


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating subscriptions."""

    class Meta:
        model = Subscription
        fields = ['plan']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
