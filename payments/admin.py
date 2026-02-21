from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_id', 'created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model."""
    list_display = [
        'invoice_number', 'client', 'case',
        'total_amount', 'status', 'issue_date', 'due_date'
    ]
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = [
        'invoice_number', 'client__email',
        'client__first_name', 'description'
    ]
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    readonly_fields = ['invoice_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline, PaymentInline]
    
    fieldsets = (
        ('Invoice Info', {
            'fields': ('invoice_number', 'client', 'case', 'description')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Status & Dates', {
            'fields': ('status', 'issue_date', 'due_date', 'paid_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceItem model."""
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'amount']
    search_fields = ['invoice__invoice_number', 'description']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    list_display = [
        'payment_id', 'invoice', 'client',
        'amount', 'payment_method', 'status', 'payment_date'
    ]
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = [
        'payment_id', 'invoice__invoice_number',
        'client__email', 'transaction_id'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('payment_id', 'invoice', 'client', 'amount')
        }),
        ('Method & Status', {
            'fields': ('payment_method', 'status', 'transaction_id')
        }),
        ('Dates', {
            'fields': ('payment_date',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
