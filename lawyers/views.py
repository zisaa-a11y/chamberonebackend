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
    LawyerCreateUpdateSerializer,
    LawyerSnakeCaseCreateSerializer,
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
    """API endpoint to list all active lawyers in snake_case format."""
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
    """API endpoint for lawyer detail in camelCase format."""
    queryset = LawyerProfile.objects.select_related('user').prefetch_related(
        'practice_areas', 'availabilities'
    )
    serializer_class = LawyerCreateUpdateSerializer
    permission_classes = [permissions.AllowAny]


class LawyerProfileUpdateView(generics.RetrieveUpdateAPIView):
    """API endpoint for lawyers to update their own profile."""
    serializer_class = LawyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return LawyerProfile.objects.get(user=self.request.user)


class LawyerCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new lawyer.
    Accepts snake_case payload (per API contract).
    
    POST /api/lawyers/create/
    """
    serializer_class = LawyerSnakeCaseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class LawyerUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update a lawyer profile (admin or self).
    
    PUT/PATCH /api/lawyers/<id>/update/
    """
    serializer_class = LawyerCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LawyerProfile.objects.all()
    
    def get_object(self):
        lawyer_id = self.kwargs.get('pk')
        lawyer = LawyerProfile.objects.get(pk=lawyer_id)
        
        # Allow admin or the lawyer themselves
        if not self.request.user.is_staff and lawyer.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own profile.")
        
        return lawyer


class LawyerCamelCaseDetailView(generics.RetrieveAPIView):
    """
    API endpoint to get lawyer detail in camelCase format.
    
    GET /api/lawyers/<id>/camelcase/
    
    Response:
    {
        "id": 1,
        "fullName": "John Doe",
        "profession": "Senior Advocate",
        "bio": "...",
        "practiceAreas": ["Criminal Law"],
        "email": "john@example.com",
        "phone": "+8801712345678",
        "yearsExperience": 15,
        "casesSolved": 500,
        "profileImage": "/media/profiles/...",
        "rating": 4.8,
        "isAvailable": true
    }
    """
    serializer_class = LawyerCreateUpdateSerializer
    permission_classes = [permissions.AllowAny]
    queryset = LawyerProfile.objects.select_related('user').prefetch_related('practice_areas')


class LawyerCamelCaseListView(generics.ListAPIView):
    """
    API endpoint to list all lawyers in camelCase format.
    
    GET /api/lawyers/list/camelcase/
    """
    serializer_class = LawyerCreateUpdateSerializer
    permission_classes = [permissions.AllowAny]
    queryset = LawyerProfile.objects.filter(
        user__is_active=True,
        is_available=True
    ).select_related('user').prefetch_related('practice_areas')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'practice_areas__name']
    ordering = ['-rating']


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
