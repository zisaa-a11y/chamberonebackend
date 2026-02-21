from django.db import models


class SiteSettings(models.Model):
    """Model for site-wide settings."""
    site_name = models.CharField(max_length=100, default='The Chamber One')
    tagline = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Social Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Only one SiteSettings instance is allowed')
        super().save(*args, **kwargs)


class HeroSection(models.Model):
    """Model for hero/banner sections."""
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    background_image = models.ImageField(
        upload_to='hero/',
        blank=True,
        null=True
    )
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero Section'
        verbose_name_plural = 'Hero Sections'
        ordering = ['order']

    def __str__(self):
        return self.title


class Service(models.Model):
    """Model for services/features displayed on landing page."""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, blank=True)
    icon_image = models.ImageField(upload_to='services/', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['order']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Model for client testimonials."""
    client_name = models.CharField(max_length=100)
    client_title = models.CharField(max_length=100, blank=True)
    client_company = models.CharField(max_length=100, blank=True)
    client_photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['order']

    def __str__(self):
        return f"{self.client_name} - {self.rating}/5"


class FAQ(models.Model):
    """Model for Frequently Asked Questions."""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order']

    def __str__(self):
        return self.question


class TeamMember(models.Model):
    """Model for team members displayed on About page."""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.title}"


class ContactSubmission(models.Model):
    """Model for contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Partner(models.Model):
    """Model for partner/client logos."""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/')
    website_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'
        ordering = ['order']

    def __str__(self):
        return self.name


class Statistic(models.Model):
    """Model for statistics/counters displayed on landing page."""
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    icon_name = models.CharField(max_length=50, blank=True)
    suffix = models.CharField(max_length=20, blank=True, help_text="e.g., +, %, K")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Statistic'
        verbose_name_plural = 'Statistics'
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}{self.suffix}"
