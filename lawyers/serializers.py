from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import PracticeArea, LawyerProfile, LawyerAvailability


class PracticeAreaSerializer(serializers.ModelSerializer):
    """Serializer for PracticeArea model."""
    
    class Meta:
        model = PracticeArea
        fields = [
            'id', 'name', 'description', 'icon_name',
            'detailed_description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LawyerAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for LawyerAvailability model."""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = LawyerAvailability
        fields = [
            'id', 'lawyer', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'is_active'
        ]
        read_only_fields = ['id']


class LawyerProfileSerializer(serializers.ModelSerializer):
    """Serializer for LawyerProfile model."""
    user = UserSerializer(read_only=True)
    practice_areas = PracticeAreaSerializer(many=True, read_only=True)
    practice_area_ids = serializers.PrimaryKeyRelatedField(
        queryset=PracticeArea.objects.all(),
        many=True,
        write_only=True,
        source='practice_areas',
        required=False
    )
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    phone = serializers.ReadOnlyField()
    profile_photo_url = serializers.ReadOnlyField()
    availabilities = LawyerAvailabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = LawyerProfile
        fields = [
            'id', 'user', 'practice_areas', 'practice_area_ids',
            'years_experience', 'solved_cases', 'consultancy_fees',
            'qualifications', 'bio', 'chamber_info', 'rating',
            'is_available', 'full_name', 'email', 'phone',
            'profile_photo_url', 'availabilities',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating']


class LawyerProfileListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing lawyers."""
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    profile_photo_url = serializers.ReadOnlyField()
    practice_areas = PracticeAreaSerializer(many=True, read_only=True)
    
    class Meta:
        model = LawyerProfile
        fields = [
            'id', 'full_name', 'email', 'profile_photo_url',
            'practice_areas', 'years_experience', 'consultancy_fees',
            'rating', 'is_available', 'chamber_info'
        ]
