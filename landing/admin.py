from django.contrib import admin
from .models import (
    SiteSettings, HeroSection, Service, Testimonial,
    FAQ, TeamMember, ContactSubmission, Partner, Statistic
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for SiteSettings model."""
    list_display = ['site_name', 'email', 'phone', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('site_name', 'tagline', 'logo', 'favicon')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': (
                'facebook_url', 'twitter_url', 'linkedin_url',
                'instagram_url', 'youtube_url'
            )
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    """Admin configuration for HeroSection model."""
    list_display = ['title', 'is_active', 'order', 'updated_at']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'subtitle']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin configuration for Service model."""
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'description']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin configuration for Testimonial model."""
    list_display = ['client_name', 'client_company', 'rating', 'is_active', 'order']
    list_filter = ['is_active', 'rating']
    list_editable = ['is_active', 'order']
    search_fields = ['client_name', 'client_company', 'content']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin configuration for FAQ model."""
    list_display = ['question', 'category', 'is_active', 'order']
    list_filter = ['is_active', 'category']
    list_editable = ['is_active', 'order']
    search_fields = ['question', 'answer']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin configuration for TeamMember model."""
    list_display = ['name', 'title', 'is_active', 'order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'title', 'bio']


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for ContactSubmission model."""
    list_display = ['name', 'email', 'subject', 'is_read', 'is_replied', 'created_at']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_replied']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_replied(self, request, queryset):
        queryset.update(is_replied=True, is_read=True)
    mark_as_replied.short_description = "Mark selected as replied"


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin configuration for Partner model."""
    list_display = ['name', 'is_active', 'order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['name']


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    """Admin configuration for Statistic model."""
    list_display = ['label', 'value', 'suffix', 'is_active', 'order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'order']
