from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment
from accounts.serializers import UserSerializer
from cases.serializers import CaseListSerializer


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
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'invoice', 'client', 'client_name',
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
    
    class Meta:
        model = Invoice
        fields = [
            'client', 'case', 'description',
            'subtotal', 'tax_amount',
            'status', 'issue_date', 'due_date', 'notes', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
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


class InvoiceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing invoices."""
    client_name = serializers.ReadOnlyField()
    case_title = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'case_title',
            'total_amount', 'status', 'status_display',
            'issue_date', 'due_date'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'payment_method', 'notes']

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)
