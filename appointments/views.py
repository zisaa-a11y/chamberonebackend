from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone

from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer,
    AppointmentListSerializer,
)


class IsOwnerOrLawyer(permissions.BasePermission):
    """Allow access only to appointment owner or the lawyer."""
    def has_object_permission(self, request, view, obj):
        return (
            obj.client == request.user or 
            obj.lawyer.user == request.user or
            request.user.is_staff
        )


class AppointmentListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create appointments."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related(
            'client', 'lawyer', 'lawyer__user'
        )
        
        # Filter based on user role
        if hasattr(user, 'lawyer_profile'):
            # Lawyer sees their appointments
            queryset = queryset.filter(lawyer=user.lawyer_profile)
        else:
            # Client sees their appointments
            queryset = queryset.filter(client=user)
        
        # Optional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() == 'true':
            queryset = queryset.filter(date_time__gte=timezone.now())
        
        return queryset


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for appointment detail."""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrLawyer]
    queryset = Appointment.objects.select_related(
        'client', 'lawyer', 'lawyer__user'
    )

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer


class AppointmentStatusUpdateView(APIView):
    """API endpoint to update appointment status."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if not (
            appointment.client == user or 
            appointment.lawyer.user == user or 
            user.is_staff
        ):
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Appointment.Status.choices):
            return Response(
                {'error': 'Invalid status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = new_status
        appointment.save()
        
        return Response(AppointmentSerializer(appointment).data)


class UpcomingAppointmentsView(generics.ListAPIView):
    """API endpoint for upcoming appointments."""
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(
            date_time__gte=timezone.now(),
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).select_related('client', 'lawyer', 'lawyer__user')
        
        if hasattr(user, 'lawyer_profile'):
            queryset = queryset.filter(lawyer=user.lawyer_profile)
        else:
            queryset = queryset.filter(client=user)
        
        return queryset.order_by('date_time')[:10]


class LawyerAppointmentsView(generics.ListAPIView):
    """API endpoint to view a specific lawyer's appointments (for clients)."""
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lawyer_id = self.kwargs.get('lawyer_id')
        return Appointment.objects.filter(
            lawyer_id=lawyer_id,
            client=self.request.user
        ).select_related('client', 'lawyer', 'lawyer__user')
