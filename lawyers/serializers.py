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
            'profile_photo_url', 'availabilities', 'gender',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating']


class LawyerProfileListSerializer(serializers.ModelSerializer):
    """Serializer for listing lawyers (snake_case, matching API contract)."""
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    phone = serializers.ReadOnlyField()
    profile_photo_url = serializers.ReadOnlyField()
    practice_areas = PracticeAreaSerializer(many=True, read_only=True)
    
    class Meta:
        model = LawyerProfile
        fields = [
            'id', 'full_name', 'email', 'phone', 'profile_photo_url',
            'practice_areas', 'years_experience', 'consultancy_fees',
            'rating', 'is_available', 'bio', 'profession',
            'specialization', 'solved_cases', 'gender',
        ]


class LawyerSnakeCaseCreateSerializer(serializers.Serializer):
    """
    Serializer for creating lawyer with snake_case fields (per API contract).
    
    Accepts both snake_case and camelCase field names.
    """
    full_name = serializers.CharField(max_length=200, required=False, default='')
    fullName = serializers.CharField(max_length=200, required=False, default='')
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    bio = serializers.CharField(required=False, allow_blank=True, default='')
    profession = serializers.CharField(max_length=100, required=False, default='Lawyer')
    specialization = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    gender = serializers.ChoiceField(choices=['male', 'female', ''], required=False, default='')
    practice_areas = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    practiceAreas = serializers.CharField(required=False, allow_blank=True, default='')
    years_experience = serializers.IntegerField(min_value=0, required=False, default=0)
    yearsExperience = serializers.IntegerField(min_value=0, required=False, default=0)
    cases_solved = serializers.IntegerField(min_value=0, required=False, default=0)
    casesSolved = serializers.IntegerField(min_value=0, required=False, default=0)
    consultancy_fees = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    profile_image = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    profileImage = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='')
    is_available = serializers.BooleanField(required=False, default=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, default='')

    def _get(self, data, snake, camel, default=None):
        """Get value preferring snake_case over camelCase."""
        val = data.get(snake)
        if val is None or val == '' or val == 0:
            val = data.get(camel, default)
        return val if val is not None else default

    def create(self, validated_data):
        from accounts.models import User
        import base64
        from django.core.files.base import ContentFile

        name = self._get(validated_data, 'full_name', 'fullName', '')
        name_parts = name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        email = validated_data['email']
        password = validated_data.get('password', '')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': validated_data.get('phone', ''),
                'role': User.Role.LAWYER,
            }
        )
        if created and password:
            user.set_password(password)
            user.save()
        elif not created:
            user.first_name = first_name
            user.last_name = last_name
            user.phone = validated_data.get('phone', '')
            user.save()

        # Handle profile image
        img = self._get(validated_data, 'profile_image', 'profileImage', '')
        if img and isinstance(img, str) and img.startswith('data:image'):
            fmt, imgstr = img.split(';base64,')
            ext = fmt.split('/')[-1]
            user.profile_photo = ContentFile(
                base64.b64decode(imgstr),
                name=f'profile_{user.id}.{ext}'
            )
            user.save()

        lawyer_profile, _ = LawyerProfile.objects.get_or_create(user=user)
        lawyer_profile.profession = validated_data.get('profession', 'Lawyer')
        lawyer_profile.specialization = validated_data.get('specialization', '')
        lawyer_profile.bio = validated_data.get('bio', '')
        lawyer_profile.gender = validated_data.get('gender', '')
        lawyer_profile.years_experience = self._get(validated_data, 'years_experience', 'yearsExperience', 0)
        lawyer_profile.solved_cases = self._get(validated_data, 'cases_solved', 'casesSolved', 0)
        fees = validated_data.get('consultancy_fees', 0)
        if fees:
            lawyer_profile.consultancy_fees = fees
        lawyer_profile.is_available = validated_data.get('is_available', True)
        lawyer_profile.save()

        # Handle practice areas (accept list or comma-separated string)
        pa_list = validated_data.get('practice_areas', [])
        pa_camel = validated_data.get('practiceAreas', '')
        if not pa_list and pa_camel:
            if isinstance(pa_camel, list):
                pa_list = pa_camel
            elif isinstance(pa_camel, str) and pa_camel.strip():
                pa_list = [a.strip() for a in pa_camel.split(',') if a.strip()]
        if pa_list:
            areas = []
            for name in pa_list:
                pa, _ = PracticeArea.objects.get_or_create(name=name)
                areas.append(pa)
            lawyer_profile.practice_areas.set(areas)

        return lawyer_profile

    def to_representation(self, instance):
        """Return created lawyer in snake_case format."""
        practice_areas = [{'name': pa.name} for pa in instance.practice_areas.all()]
        user = instance.user
        profile_image = None
        try:
            if user.profile_photo:
                profile_image = user.profile_photo.url
        except Exception:
            pass
        return {
            'id': instance.id,
            'full_name': user.full_name,
            'practice_areas': practice_areas,
            'years_experience': instance.years_experience,
            'consultancy_fees': float(instance.consultancy_fees),
            'email': user.email,
            'phone': user.phone or '',
            'profession': instance.profession,
            'bio': instance.bio or '',
            'profile_photo_url': profile_image,
            'rating': float(instance.rating) if instance.rating else 0.0,
            'is_available': instance.is_available,
            'specialization': instance.specialization or '',
            'solved_cases': instance.solved_cases,
            'gender': instance.gender or '',
        }


class LawyerCreateUpdateSerializer(serializers.Serializer):
    """
    Serializer for creating/updating lawyer with camelCase fields.
    
    Expected JSON format:
    {
        "fullName": "John Doe",
        "profession": "Senior Advocate",
        "bio": "Experienced lawyer...",
        "practiceAreas": ["Criminal Law", "Family Law"],
        "email": "john@example.com",
        "phone": "+8801712345678",
        "yearsExperience": 15,
        "casesSolved": 500,
        "profileImage": "<base64 string or null>"
    }
    
    For HTML form, practiceAreas can be comma-separated: "Criminal Law, Family Law"
    """
    fullName = serializers.CharField(
        max_length=200, 
        help_text="Full name of the lawyer",
        style={'placeholder': 'e.g. John Doe'}
    )
    profession = serializers.CharField(
        max_length=100, 
        required=False, 
        default='Lawyer',
        help_text="e.g. Senior Advocate, Barrister"
    )
    specialization = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='',
        help_text="e.g. Civil Law, Criminal Law"
    )
    bio = serializers.CharField(
        required=False, 
        allow_blank=True, 
        default='',
        style={'base_template': 'textarea.html'},
        help_text="Short biography"
    )
    practiceAreas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Comma-separated: Criminal Law, Family Law, Corporate Law"
    )
    email = serializers.EmailField(
        help_text="Email address (will be used as username)"
    )
    phone = serializers.CharField(
        max_length=20, 
        required=False, 
        allow_blank=True, 
        default='',
        help_text="+8801XXXXXXXXX"
    )
    yearsExperience = serializers.IntegerField(
        min_value=0, 
        default=0,
        help_text="Years of experience"
    )
    casesSolved = serializers.IntegerField(
        min_value=0, 
        default=0,
        help_text="Number of cases solved"
    )
    profileImage = serializers.CharField(
        required=False, 
        allow_null=True, 
        allow_blank=True,
        help_text="Base64 image or leave blank"
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'},
        help_text="Password for new lawyer account (optional)"
    )
    
    def validate_practiceAreas(self, value):
        """Convert comma-separated string to list or accept list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            if not value.strip():
                return []
            return [area.strip() for area in value.split(',') if area.strip()]
        return []
    
    def create(self, validated_data):
        from accounts.models import User
        import base64
        from django.core.files.base import ContentFile
        
        # Split full name
        full_name = validated_data.get('fullName', '')
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create or get user
        email = validated_data['email']
        password = validated_data.get('password', '')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': validated_data.get('phone', ''),
                'role': User.Role.LAWYER,
            }
        )
        
        if created and password:
            user.set_password(password)
            user.save()
        elif not created:
            user.first_name = first_name
            user.last_name = last_name
            user.phone = validated_data.get('phone', '')
            user.save()
        
        # Handle profile image
        profile_image_data = validated_data.get('profileImage')
        if profile_image_data and profile_image_data.startswith('data:image'):
            # Parse base64 image
            format, imgstr = profile_image_data.split(';base64,')
            ext = format.split('/')[-1]
            user.profile_photo = ContentFile(
                base64.b64decode(imgstr), 
                name=f'profile_{user.id}.{ext}'
            )
            user.save()
        
        # Create or update lawyer profile
        lawyer_profile, _ = LawyerProfile.objects.get_or_create(user=user)
        lawyer_profile.profession = validated_data.get('profession', 'Lawyer')
        lawyer_profile.specialization = validated_data.get('specialization', '')
        lawyer_profile.bio = validated_data.get('bio', '')
        lawyer_profile.years_experience = validated_data.get('yearsExperience', 0)
        lawyer_profile.solved_cases = validated_data.get('casesSolved', 0)
        lawyer_profile.save()
        
        # Handle practice areas
        practice_area_names = validated_data.get('practiceAreas', [])
        if practice_area_names:
            practice_areas = []
            for name in practice_area_names:
                pa, _ = PracticeArea.objects.get_or_create(name=name)
                practice_areas.append(pa)
            lawyer_profile.practice_areas.set(practice_areas)
        
        return lawyer_profile
    
    def update(self, instance, validated_data):
        from accounts.models import User
        import base64
        from django.core.files.base import ContentFile
        
        user = instance.user
        
        # Update name
        full_name = validated_data.get('fullName', '')
        if full_name:
            name_parts = full_name.strip().split(' ', 1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Update phone
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        
        # Handle profile image
        profile_image_data = validated_data.get('profileImage')
        if profile_image_data and profile_image_data.startswith('data:image'):
            format, imgstr = profile_image_data.split(';base64,')
            ext = format.split('/')[-1]
            user.profile_photo = ContentFile(
                base64.b64decode(imgstr), 
                name=f'profile_{user.id}.{ext}'
            )
        
        user.save()
        
        # Update lawyer profile
        if 'profession' in validated_data:
            instance.profession = validated_data['profession']
        if 'specialization' in validated_data:
            instance.specialization = validated_data['specialization']
        if 'bio' in validated_data:
            instance.bio = validated_data['bio']
        if 'yearsExperience' in validated_data:
            instance.years_experience = validated_data['yearsExperience']
        if 'casesSolved' in validated_data:
            instance.solved_cases = validated_data['casesSolved']
        
        instance.save()
        
        # Handle practice areas
        practice_area_names = validated_data.get('practiceAreas')
        if practice_area_names is not None:
            practice_areas = []
            for name in practice_area_names:
                pa, _ = PracticeArea.objects.get_or_create(name=name)
                practice_areas.append(pa)
            instance.practice_areas.set(practice_areas)
        
        return instance
    
    def to_representation(self, instance):
        """Convert LawyerProfile to camelCase JSON format."""
        try:
            practice_areas = [pa.name for pa in instance.practice_areas.all()]
            user = instance.user
            
            profile_image = None
            try:
                if user.profile_photo:
                    profile_image = user.profile_photo.url
            except Exception:
                profile_image = None
            
            return {
                'id': instance.id,
                'fullName': user.full_name,
                'profession': getattr(instance, 'profession', 'Lawyer'),
                'bio': instance.bio or '',
                'practiceAreas': practice_areas,
                'specialization': instance.specialization or '',
                'email': user.email,
                'phone': user.phone or '',
                'yearsExperience': instance.years_experience,
                'casesSolved': instance.solved_cases,
                'profileImage': profile_image,
                'rating': float(instance.rating) if instance.rating else 0.0,
                'isAvailable': instance.is_available,
            }
        except Exception as e:
            return {
                'id': instance.id,
                'fullName': 'Unknown',
                'profession': 'Lawyer',
                'bio': '',
                'practiceAreas': [],
                'specialization': getattr(instance, 'specialization', ''),
                'email': '',
                'phone': '',
                'yearsExperience': 0,
                'casesSolved': 0,
                'profileImage': None,
                'rating': 0.0,
                'isAvailable': False,
            }

