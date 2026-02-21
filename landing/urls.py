from django.urls import path
from .views import (
    LandingPageView,
    SiteSettingsView,
    HeroSectionListCreateView,
    HeroSectionDetailView,
    ServiceListCreateView,
    ServiceDetailView,
    TestimonialListCreateView,
    TestimonialDetailView,
    FAQListCreateView,
    FAQDetailView,
    TeamMemberListCreateView,
    TeamMemberDetailView,
    ContactSubmissionCreateView,
    ContactSubmissionListView,
    ContactSubmissionDetailView,
    ContactSubmissionMarkReadView,
    PartnerListCreateView,
    PartnerDetailView,
    StatisticListCreateView,
    StatisticDetailView,
)

app_name = 'landing'

urlpatterns = [
    # Combined landing page data
    path('', LandingPageView.as_view(), name='landing_page'),
    
    # Site Settings
    path('settings/', SiteSettingsView.as_view(), name='site_settings'),
    
    # Hero Sections
    path('hero/', HeroSectionListCreateView.as_view(), name='hero_list'),
    path('hero/<int:pk>/', HeroSectionDetailView.as_view(), name='hero_detail'),
    
    # Services
    path('services/', ServiceListCreateView.as_view(), name='service_list'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service_detail'),
    
    # Testimonials
    path('testimonials/', TestimonialListCreateView.as_view(), name='testimonial_list'),
    path('testimonials/<int:pk>/', TestimonialDetailView.as_view(), name='testimonial_detail'),
    
    # FAQs
    path('faqs/', FAQListCreateView.as_view(), name='faq_list'),
    path('faqs/<int:pk>/', FAQDetailView.as_view(), name='faq_detail'),
    
    # Team Members
    path('team/', TeamMemberListCreateView.as_view(), name='team_list'),
    path('team/<int:pk>/', TeamMemberDetailView.as_view(), name='team_detail'),
    
    # Contact Submissions
    path('contact/', ContactSubmissionCreateView.as_view(), name='contact_create'),
    path('contact/list/', ContactSubmissionListView.as_view(), name='contact_list'),
    path('contact/<int:pk>/', ContactSubmissionDetailView.as_view(), name='contact_detail'),
    path('contact/<int:pk>/read/', ContactSubmissionMarkReadView.as_view(), name='contact_mark_read'),
    
    # Partners
    path('partners/', PartnerListCreateView.as_view(), name='partner_list'),
    path('partners/<int:pk>/', PartnerDetailView.as_view(), name='partner_detail'),
    
    # Statistics
    path('statistics/', StatisticListCreateView.as_view(), name='statistic_list'),
    path('statistics/<int:pk>/', StatisticDetailView.as_view(), name='statistic_detail'),
]
