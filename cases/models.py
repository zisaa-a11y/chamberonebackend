from django.db import models
from django.conf import settings
import uuid


class Case(models.Model):
    """Model for legal cases."""
    
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        PENDING = 'pending', 'Pending'
        CLOSED = 'closed', 'Closed'
    
    title = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    case_number = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    court_name = models.CharField(max_length=255, blank=True)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cases'
    )
    lawyer = models.ForeignKey(
        'lawyers.LawyerProfile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='cases'
    )
    practice_area = models.ForeignKey(
        'lawyers.PracticeArea',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cases'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    next_hearing_date = models.DateTimeField(null=True, blank=True)
    filing_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Case'
        verbose_name_plural = 'Cases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['lawyer', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.case_number:
            # Generate unique case number
            self.case_number = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        if not self.client_name and self.client_id:
            self.client_name = self.client.full_name
        super().save(*args, **kwargs)

    @property
    def case_title(self):
        return self.title

    @property
    def lawyer_name(self):
        return self.lawyer.full_name if self.lawyer else None


class CaseDocument(models.Model):
    """Model for documents attached to cases."""
    
    class DocumentType(models.TextChoices):
        EVIDENCE = 'evidence', 'Evidence'
        CONTRACT = 'contract', 'Contract'
        COURT_ORDER = 'court_order', 'Court Order'
        LEGAL_BRIEF = 'legal_brief', 'Legal Brief'
        CORRESPONDENCE = 'correspondence', 'Correspondence'
        OTHER = 'other', 'Other'
    
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=255, blank=True)
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )
    file = models.FileField(upload_to='case_documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    original_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Case Document'
        verbose_name_plural = 'Case Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['case', '-created_at']),
        ]

    def __str__(self):
        return f"{self.case.case_number} - {self.title}"

    @property
    def uploaded_at(self):
        return self.created_at


class CaseTimeline(models.Model):
    """Model for case timeline events."""
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='timeline'
    )
    date = models.DateField()
    event = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Case Timeline Event'
        verbose_name_plural = 'Case Timeline Events'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['case', '-date']),
        ]

    def __str__(self):
        return f"{self.case.case_number} - {self.event}"


class CaseNote(models.Model):
    """Model for internal notes on cases."""
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='case_notes'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    content = models.TextField()
    is_private = models.BooleanField(
        default=False,
        help_text="Private notes are only visible to lawyers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Case Note'
        verbose_name_plural = 'Case Notes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.case.case_number}"
