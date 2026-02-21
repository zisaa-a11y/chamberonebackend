from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    SiteSettings, HeroSection, Service, Testimonial,
    FAQ, TeamMember, ContactSubmission, Partner, Statistic
)
from .serializers import (
    SiteSettingsSerializer,
    HeroSectionSerializer,
    ServiceSerializer,
    TestimonialSerializer,
    FAQSerializer,
    TeamMemberSerializer,
    ContactSubmissionSerializer,
    ContactSubmissionCreateSerializer,
    PartnerSerializer,
    StatisticSerializer,
    LandingPageSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for everyone, write only for admins."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# Combined Landing Page View
class LandingPageView(APIView):
    """API endpoint to get all landing page data in one request."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        site_settings = SiteSettings.objects.first()
        hero_sections = HeroSection.objects.filter(is_active=True)
        services = Service.objects.filter(is_active=True)
        testimonials = Testimonial.objects.filter(is_active=True)
        faqs = FAQ.objects.filter(is_active=True)
        team_members = TeamMember.objects.filter(is_active=True)
        partners = Partner.objects.filter(is_active=True)
        statistics = Statistic.objects.filter(is_active=True)

        data = {
            'site_settings': SiteSettingsSerializer(site_settings).data if site_settings else None,
            'hero_sections': HeroSectionSerializer(hero_sections, many=True).data,
            'services': ServiceSerializer(services, many=True).data,
            'testimonials': TestimonialSerializer(testimonials, many=True).data,
            'faqs': FAQSerializer(faqs, many=True).data,
            'team_members': TeamMemberSerializer(team_members, many=True).data,
            'partners': PartnerSerializer(partners, many=True).data,
            'statistics': StatisticSerializer(statistics, many=True).data,
        }

        return Response(data)


# Site Settings Views
class SiteSettingsView(generics.RetrieveUpdateAPIView):
    """API endpoint for site settings."""
    serializer_class = SiteSettingsSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        obj, created = SiteSettings.objects.get_or_create(pk=1)
        return obj


# Hero Section Views
class HeroSectionListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create hero sections."""
    queryset = HeroSection.objects.filter(is_active=True)
    serializer_class = HeroSectionSerializer
    permission_classes = [IsAdminOrReadOnly]


class HeroSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for hero section detail."""
    queryset = HeroSection.objects.all()
    serializer_class = HeroSectionSerializer
    permission_classes = [IsAdminOrReadOnly]


# Service Views
class ServiceListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create services."""
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for service detail."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]


# Testimonial Views
class TestimonialListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create testimonials."""
    queryset = Testimonial.objects.filter(is_active=True)
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]


class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for testimonial detail."""
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]


# FAQ Views
class FAQListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create FAQs."""
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for FAQ detail."""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]


# Team Member Views
class TeamMemberListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create team members."""
    queryset = TeamMember.objects.filter(is_active=True)
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAdminOrReadOnly]


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for team member detail."""
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAdminOrReadOnly]


# Contact Submission Views
class ContactSubmissionCreateView(generics.CreateAPIView):
    """API endpoint to create contact submissions (public)."""
    serializer_class = ContactSubmissionCreateSerializer
    permission_classes = [permissions.AllowAny]


class ContactSubmissionListView(generics.ListAPIView):
    """API endpoint to list contact submissions (admin only)."""
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    permission_classes = [permissions.IsAdminUser]


class ContactSubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for contact submission detail (admin only)."""
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    permission_classes = [permissions.IsAdminUser]


class ContactSubmissionMarkReadView(APIView):
    """API endpoint to mark contact submission as read."""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            submission = ContactSubmission.objects.get(pk=pk)
        except ContactSubmission.DoesNotExist:
            return Response(
                {'error': 'Submission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        submission.is_read = True
        submission.save()
        
        return Response(ContactSubmissionSerializer(submission).data)


# Partner Views
class PartnerListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create partners."""
    queryset = Partner.objects.filter(is_active=True)
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]


class PartnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for partner detail."""
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]


# Statistic Views
class StatisticListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create statistics."""
    queryset = Statistic.objects.filter(is_active=True)
    serializer_class = StatisticSerializer
    permission_classes = [IsAdminOrReadOnly]


class StatisticDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for statistic detail."""
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer
    permission_classes = [IsAdminOrReadOnly]
