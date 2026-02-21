from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ClientProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    list_display = [
        'email', 'first_name', 'last_name', 'role',
        'is_active', 'is_verified', 'created_at'
    ]
    list_filter = ['role', 'is_active', 'is_verified', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'profile_photo')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'password1', 'password2',
                'role', 'is_active', 'is_staff'
            ),
        }),
    )


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """Admin configuration for ClientProfile model."""
    list_display = ['user', 'company_name']
    search_fields = ['user__email', 'user__first_name', 'company_name']
