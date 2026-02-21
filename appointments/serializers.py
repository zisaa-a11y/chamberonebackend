from rest_framework import serializers
from .models import Appointment
from accounts.serializers import UserSerializer
from lawyers.serializers import LawyerProfileListSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """Full serializer for Appointment model."""
    client = UserSerializer(read_only=True)
    lawyer_details = LawyerProfileListSerializer(source='lawyer', read_only=True)
    client_name = serializers.ReadOnlyField()
    lawyer_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'lawyer', 'lawyer_details',
            'client_name', 'lawyer_name',
            'date_time', 'duration_minutes',
            'status', 'status_display',
            'appointment_type', 'type_display',
            'notes', 'client_notes', 'meeting_link',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments."""
    
    class Meta:
        model = Appointment
        fields = [
            'lawyer', 'date_time', 'duration_minutes',
            'appointment_type', 'client_notes'
        ]

    def validate_date_time(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError(
                "Appointment date cannot be in the past."
            )
        return value

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments."""
    
    class Meta:
        model = Appointment
        fields = [
            'date_time', 'duration_minutes', 'status',
            'appointment_type', 'notes', 'client_notes',
            'lawyer_notes', 'meeting_link'
        ]


class AppointmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing appointments."""
    client_name = serializers.ReadOnlyField()
    lawyer_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client_name', 'lawyer_name',
            'date_time', 'duration_minutes',
            'status', 'status_display',
            'appointment_type', 'type_display'
        ]
