from django.db import models
from django.conf import settings


class Appointment(models.Model):
    """Model for client appointments with lawyers."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
        NO_SHOW = 'no_show', 'No Show'
    
    class AppointmentType(models.TextChoices):
        CONSULTATION = 'consultation', 'Consultation'
        FOLLOW_UP = 'follow_up', 'Follow Up'
        CASE_REVIEW = 'case_review', 'Case Review'
        DOCUMENT_REVIEW = 'document_review', 'Document Review'
        OTHER = 'other', 'Other'
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_appointments'
    )
    lawyer = models.ForeignKey(
        'lawyers.LawyerProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    date_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=AppointmentType.choices,
        default=AppointmentType.CONSULTATION
    )
    notes = models.TextField(blank=True)
    client_notes = models.TextField(blank=True, help_text="Notes from client")
    lawyer_notes = models.TextField(blank=True, help_text="Private notes from lawyer")
    meeting_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.client.full_name} - {self.lawyer.full_name} - {self.date_time}"

    @property
    def client_name(self):
        return self.client.full_name

    @property
    def lawyer_name(self):
        return self.lawyer.full_name
