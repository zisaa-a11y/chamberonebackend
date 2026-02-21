from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin configuration for Appointment model."""
    list_display = [
        'id', 'client', 'lawyer', 'date_time',
        'status', 'appointment_type', 'created_at'
    ]
    list_filter = ['status', 'appointment_type', 'date_time']
    search_fields = [
        'client__email', 'client__first_name',
        'lawyer__user__email', 'lawyer__user__first_name',
        'notes'
    ]
    date_hierarchy = 'date_time'
    ordering = ['-date_time']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Info', {
            'fields': ('client', 'lawyer', 'date_time', 'duration_minutes')
        }),
        ('Status', {
            'fields': ('status', 'appointment_type')
        }),
        ('Notes', {
            'fields': ('notes', 'client_notes', 'lawyer_notes', 'meeting_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
