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
    created_by = serializers.ReadOnlyField(source='created_by.id')
    
    class Meta:
        model = CaseTimeline
        fields = [
            'id', 'case', 'date', 'event', 'description',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'case', 'created_at', 'created_by']

    def validate_event(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        return value


class CaseDocumentSerializer(serializers.ModelSerializer):
    """Serializer for CaseDocument model."""
    document = serializers.FileField(write_only=True, required=False)
    file_url = serializers.SerializerMethodField(read_only=True)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.id')
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.full_name',
        read_only=True
    )

    class Meta:
        model = CaseDocument
        fields = [
            'id', 'case', 'title', 'document_type',
            'document', 'file', 'file_url', 'original_name',
            'description', 'uploaded_at', 'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'uploaded_by']
        extra_kwargs = {
            'case': {'required': False},
            'file': {'required': False},
        }

    def get_file_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def validate(self, attrs):
        uploaded = attrs.get('document') or attrs.get('file')
        if self.instance is None and uploaded is None:
            raise serializers.ValidationError({'document': ['This field is required.']})

        if uploaded is not None:
            allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
            file_name = uploaded.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise serializers.ValidationError({
                    'document': ['Unsupported file type. Allowed types: pdf, jpg, jpeg, png.']
                })

            max_size = 10 * 1024 * 1024
            if uploaded.size > max_size:
                raise serializers.ValidationError({
                    'document': ['File size exceeds 10MB limit.']
                })

        return attrs

    def create(self, validated_data):
        uploaded = validated_data.pop('document', None)
        if uploaded is not None:
            validated_data['file'] = uploaded
            validated_data.setdefault('title', uploaded.name)
            validated_data['original_name'] = uploaded.name
        return super().create(validated_data)


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
    case_title = serializers.CharField(source='title', read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'case_title', 'case_number', 'description',
            'court_name', 'client', 'lawyer', 'lawyer_details',
            'practice_area', 'practice_area_details',
            'client_name', 'lawyer_name',
            'status', 'status_display',
            'next_hearing_date', 'filing_date', 'closing_date',
            'notes', 'documents', 'timeline',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at']


class CaseAssignLawyerSerializer(serializers.Serializer):
    """Serializer for assigning or reassigning a lawyer to a case."""
    lawyer = serializers.IntegerField(required=False)
    assigned_lawyer = serializers.IntegerField(required=False)
    lawyer_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('lawyer') and not attrs.get('assigned_lawyer') and not attrs.get('lawyer_name'):
            raise serializers.ValidationError({
                'lawyer': 'Provide lawyer, assigned_lawyer, or lawyer_name.'
            })
        return attrs


class CaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cases."""
    case_title = serializers.CharField(source='title', required=False, allow_blank=False)
    client_name = serializers.CharField(required=True, allow_blank=False)
    title = serializers.CharField(required=True, allow_blank=False)
    court_name = serializers.CharField(required=True, allow_blank=False)
    
    class Meta:
        model = Case
        fields = [
            'title', 'case_title', 'client_name', 'description', 'court_name',
            'lawyer', 'practice_area', 'status',
            'next_hearing_date', 'filing_date', 'notes'
        ]

    def validate_client_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Client name is required.')
        return value

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Case title is required.')
        return value

    def validate_court_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Court name is required.')
        return value

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        if not validated_data.get('client_name'):
            validated_data['client_name'] = self.context['request'].user.full_name
        return super().create(validated_data)


class CaseListSerializer(serializers.ModelSerializer):
    """Contract-focused serializer for listing cases."""
    client_name = serializers.ReadOnlyField()
    lawyer_name = serializers.ReadOnlyField()
    case_title = serializers.CharField(source='title', read_only=True)
    timeline = CaseTimelineSerializer(many=True, read_only=True)
    documents = CaseDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'case_title', 'case_number', 'court_name',
            'status', 'next_hearing_date', 'client_name', 'lawyer_name',
            'timeline', 'documents'
        ]
