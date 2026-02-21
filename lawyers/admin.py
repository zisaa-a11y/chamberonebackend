from django.contrib import admin
from .models import PracticeArea, LawyerProfile, LawyerAvailability


@admin.register(PracticeArea)
class PracticeAreaAdmin(admin.ModelAdmin):
    """Admin configuration for PracticeArea model."""
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    """Admin configuration for LawyerProfile model."""
    list_display = [
        'full_name', 'email', 'years_experience',
        'consultancy_fees', 'rating', 'is_available'
    ]
    list_filter = ['is_available', 'practice_areas', 'years_experience']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'chamber_info'
    ]
    filter_horizontal = ['practice_areas']
    readonly_fields = ['created_at', 'updated_at']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'

    def email(self, obj):
        return obj.email
    email.short_description = 'Email'


@admin.register(LawyerAvailability)
class LawyerAvailabilityAdmin(admin.ModelAdmin):
    """Admin configuration for LawyerAvailability model."""
    list_display = ['lawyer', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    search_fields = ['lawyer__user__first_name', 'lawyer__user__last_name']
