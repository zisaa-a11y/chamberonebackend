from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import PracticeArea, LawyerProfile, LawyerAvailability
from .serializers import (
    PracticeAreaSerializer,
    LawyerProfileSerializer,
    LawyerProfileListSerializer,
    LawyerAvailabilitySerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for everyone, write only for admins."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# Practice Area Views
class PracticeAreaListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create practice areas."""
    queryset = PracticeArea.objects.filter(is_active=True)
    serializer_class = PracticeAreaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class PracticeAreaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for practice area detail."""
    queryset = PracticeArea.objects.all()
    serializer_class = PracticeAreaSerializer
    permission_classes = [IsAdminOrReadOnly]


# Lawyer Profile Views
class LawyerListView(generics.ListAPIView):
    """API endpoint to list all active lawyers."""
    queryset = LawyerProfile.objects.filter(
        user__is_active=True,
        is_available=True
    ).select_related('user').prefetch_related('practice_areas')
    serializer_class = LawyerProfileListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'user__first_name', 'user__last_name',
        'practice_areas__name', 'chamber_info'
    ]
    ordering_fields = ['rating', 'years_experience', 'consultancy_fees']
    ordering = ['-rating']


class LawyerDetailView(generics.RetrieveAPIView):
    """API endpoint for lawyer detail."""
    queryset = LawyerProfile.objects.select_related('user').prefetch_related(
        'practice_areas', 'availabilities'
    )
    serializer_class = LawyerProfileSerializer
    permission_classes = [permissions.AllowAny]


class LawyerProfileUpdateView(generics.RetrieveUpdateAPIView):
    """API endpoint for lawyers to update their own profile."""
    serializer_class = LawyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return LawyerProfile.objects.get(user=self.request.user)


class LawyersByPracticeAreaView(generics.ListAPIView):
    """API endpoint to list lawyers by practice area."""
    serializer_class = LawyerProfileListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        practice_area_id = self.kwargs.get('practice_area_id')
        return LawyerProfile.objects.filter(
            practice_areas__id=practice_area_id,
            user__is_active=True,
            is_available=True
        ).select_related('user').prefetch_related('practice_areas')


# Lawyer Availability Views
class LawyerAvailabilityListCreateView(generics.ListCreateAPIView):
    """API endpoint to manage lawyer availability."""
    serializer_class = LawyerAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LawyerAvailability.objects.filter(
            lawyer__user=self.request.user
        )

    def perform_create(self, serializer):
        lawyer_profile = LawyerProfile.objects.get(user=self.request.user)
        serializer.save(lawyer=lawyer_profile)


class LawyerAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for availability detail."""
    serializer_class = LawyerAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LawyerAvailability.objects.filter(
            lawyer__user=self.request.user
        )


class PublicLawyerAvailabilityView(generics.ListAPIView):
    """API endpoint to view a lawyer's availability (public)."""
    serializer_class = LawyerAvailabilitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        lawyer_id = self.kwargs.get('lawyer_id')
        return LawyerAvailability.objects.filter(
            lawyer_id=lawyer_id,
            is_active=True
        )
