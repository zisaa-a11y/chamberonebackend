from rest_framework import serializers
from .models import Case, CaseDocument, CaseTimeline, CaseNote
from accounts.serializers import UserSerializer
from lawyers.serializers import LawyerProfileListSerializer, PracticeAreaSerializer


class CaseTimelineSerializer(serializers.ModelSerializer):
    """Serializer for CaseTimeline model."""
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True
    )
    
    class Meta:
        model = CaseTimeline
        fields = [
            'id', 'case', 'date', 'event', 'description',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


class CaseDocumentSerializer(serializers.ModelSerializer):
    """Serializer for CaseDocument model."""
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.full_name',
        read_only=True
    )
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )
    
    class Meta:
        model = CaseDocument
        fields = [
            'id', 'case', 'title', 'document_type',
            'document_type_display', 'file', 'description',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'uploaded_by']


class CaseNoteSerializer(serializers.ModelSerializer):
    """Serializer for CaseNote model."""
    author_name = serializers.CharField(
        source='author.full_name',
        read_only=True
    )
    
    class Meta:
        model = CaseNote
        fields = [
            'id', 'case', 'author', 'author_name',
            'content', 'is_private', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']


class CaseSerializer(serializers.ModelSerializer):
    """Full serializer for Case model."""
    client = UserSerializer(read_only=True)
    lawyer_details = LawyerProfileListSerializer(source='lawyer', read_only=True)
    practice_area_details = PracticeAreaSerializer(source='practice_area', read_only=True)
    client_name = serializers.ReadOnlyField()
    lawyer_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)
    timeline = CaseTimelineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'case_number', 'description',
            'court_name', 'client', 'lawyer', 'lawyer_details',
            'practice_area', 'practice_area_details',
            'client_name', 'lawyer_name',
            'status', 'status_display',
            'next_hearing_date', 'filing_date', 'closing_date',
            'notes', 'documents', 'timeline',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at']


class CaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cases."""
    
    class Meta:
        model = Case
        fields = [
            'title', 'description', 'court_name',
            'lawyer', 'practice_area', 'status',
            'next_hearing_date', 'filing_date', 'notes'
        ]

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class CaseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing cases."""
    client_name = serializers.ReadOnlyField()
    lawyer_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'case_number', 'court_name',
            'client_name', 'lawyer_name',
            'status', 'status_display',
            'next_hearing_date', 'created_at'
        ]
