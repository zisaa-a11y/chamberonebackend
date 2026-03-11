from django.db import models
from django.conf import settings


class PracticeArea(models.Model):
    """Practice areas/specializations for lawyers."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=50, blank=True)
    detailed_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Practice Area'
        verbose_name_plural = 'Practice Areas'
        ordering = ['name']

    def __str__(self):
        return self.name


class LawyerProfile(models.Model):
    """Extended profile for lawyer users."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lawyer_profile'
    )
    profession = models.CharField(max_length=100, default='Lawyer', blank=True)
    specialization = models.CharField(max_length=255, blank=True, default='')
    practice_areas = models.ManyToManyField(
        PracticeArea,
        related_name='lawyers',
        blank=True
    )
    years_experience = models.PositiveIntegerField(default=0)
    solved_cases = models.PositiveIntegerField(default=0)
    consultancy_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    qualifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    chamber_info = models.TextField(blank=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=4.5
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lawyer Profile'
        verbose_name_plural = 'Lawyer Profiles'
        ordering = ['-rating', '-years_experience']

    def __str__(self):
        return f"Lawyer: {self.user.full_name}"

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email

    @property
    def phone(self):
        return self.user.phone

    @property
    def profile_photo_url(self):
        if self.user.profile_photo:
            return self.user.profile_photo.url
        return None


class LawyerAvailability(models.Model):
    """Availability slots for lawyers."""
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Lawyer Availability'
        verbose_name_plural = 'Lawyer Availabilities'
        unique_together = ['lawyer', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.lawyer.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
