from rest_framework import serializers
from .models import (
    SiteSettings, HeroSection, Service, Testimonial,
    FAQ, TeamMember, ContactSubmission, Partner, Statistic
)


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SiteSettings model."""
    
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'tagline', 'logo', 'favicon',
            'email', 'phone', 'address',
            'facebook_url', 'twitter_url', 'linkedin_url',
            'instagram_url', 'youtube_url',
            'meta_description', 'meta_keywords'
        ]


class HeroSectionSerializer(serializers.ModelSerializer):
    """Serializer for HeroSection model."""
    
    class Meta:
        model = HeroSection
        fields = [
            'id', 'title', 'subtitle', 'background_image',
            'button_text', 'button_link', 'is_active', 'order'
        ]


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model."""
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'icon_name',
            'icon_image', 'link', 'is_active', 'order'
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial model."""
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_title', 'client_company',
            'client_photo', 'content', 'rating', 'is_active', 'order'
        ]


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model."""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'is_active', 'order']


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for TeamMember model."""
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'name', 'title', 'bio', 'photo',
            'email', 'linkedin_url', 'is_active', 'order'
        ]


class ContactSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for ContactSubmission model."""
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'name', 'email', 'phone', 'subject',
            'message', 'is_read', 'is_replied', 'created_at'
        ]
        read_only_fields = ['id', 'is_read', 'is_replied', 'created_at']


class ContactSubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact submissions."""
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'phone', 'subject', 'message']


class PartnerSerializer(serializers.ModelSerializer):
    """Serializer for Partner model."""
    
    class Meta:
        model = Partner
        fields = ['id', 'name', 'logo', 'website_url', 'is_active', 'order']


class StatisticSerializer(serializers.ModelSerializer):
    """Serializer for Statistic model."""
    
    class Meta:
        model = Statistic
        fields = ['id', 'label', 'value', 'icon_name', 'suffix', 'is_active', 'order']


class LandingPageSerializer(serializers.Serializer):
    """Combined serializer for all landing page data."""
    site_settings = SiteSettingsSerializer()
    hero_sections = HeroSectionSerializer(many=True)
    services = ServiceSerializer(many=True)
    testimonials = TestimonialSerializer(many=True)
    faqs = FAQSerializer(many=True)
    team_members = TeamMemberSerializer(many=True)
    partners = PartnerSerializer(many=True)
    statistics = StatisticSerializer(many=True)
