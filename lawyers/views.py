from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

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


class IsAdminOrSelfForLawyerWrite(permissions.BasePermission):
    """Allow public read; only authenticated admin or owner can modify."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and (request.user.is_staff or obj.user == request.user))


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

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        location = params.get('location')
        city = params.get('city')
        district = params.get('district')
        practice_area = params.get('practice_area')
        gender = params.get('gender')

        if location:
            queryset = queryset.filter(location__icontains=location.strip())
        if city:
            queryset = queryset.filter(city__icontains=city.strip())
        if district:
            queryset = queryset.filter(district__icontains=district.strip())
        if practice_area:
            queryset = queryset.filter(
                Q(practice_areas__name__icontains=practice_area.strip()) |
                Q(specialization__icontains=practice_area.strip())
            )
        if gender:
            queryset = queryset.filter(gender__iexact=gender.strip())

        return queryset.distinct()


class LawyerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for lawyer detail and RESTful update/delete."""
    queryset = LawyerProfile.objects.select_related('user').prefetch_related(
        'practice_areas', 'availabilities'
    )
    permission_classes = [IsAdminOrSelfForLawyerWrite]

    def get_serializer_class(self):
        # Keep existing camelCase response for GET and support snake_case/camelCase input for writes.
        if self.request.method in permissions.SAFE_METHODS:
            return LawyerCreateUpdateSerializer
        return LawyerSnakeCaseCreateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                'success': True,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                'success': True,
                'detail': 'Lawyer deleted successfully.',
            },
            status=status.HTTP_200_OK,
        )


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
    permission_classes = [permissions.IsAdminUser]


class LawyerUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update a lawyer profile (admin or self).
    
    PUT/PATCH /api/lawyers/<id>/update/
    """
    serializer_class = LawyerSnakeCaseCreateSerializer
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
