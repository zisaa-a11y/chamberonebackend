from django.contrib import admin
from .models import Case, CaseDocument, CaseTimeline, CaseNote


class CaseDocumentInline(admin.TabularInline):
    model = CaseDocument
    extra = 0
    readonly_fields = ['created_at']


class CaseTimelineInline(admin.TabularInline):
    model = CaseTimeline
    extra = 0
    readonly_fields = ['created_at']


class CaseNoteInline(admin.TabularInline):
    model = CaseNote
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """Admin configuration for Case model."""
    list_display = [
        'case_number', 'title', 'client', 'lawyer',
        'status', 'next_hearing_date', 'created_at'
    ]
    list_filter = ['status', 'practice_area', 'created_at']
    search_fields = [
        'case_number', 'title', 'court_name',
        'client__email', 'client__first_name',
        'lawyer__user__email', 'lawyer__user__first_name'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['case_number', 'created_at', 'updated_at']
    inlines = [CaseDocumentInline, CaseTimelineInline, CaseNoteInline]
    
    fieldsets = (
        ('Case Info', {
            'fields': ('case_number', 'title', 'description', 'court_name')
        }),
        ('Parties', {
            'fields': ('client', 'lawyer', 'practice_area')
        }),
        ('Status', {
            'fields': ('status', 'next_hearing_date', 'filing_date', 'closing_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for CaseDocument model."""
    list_display = ['title', 'case', 'document_type', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'created_at']
    search_fields = ['title', 'case__case_number', 'description']


@admin.register(CaseTimeline)
class CaseTimelineAdmin(admin.ModelAdmin):
    """Admin configuration for CaseTimeline model."""
    list_display = ['event', 'case', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['event', 'case__case_number', 'description']


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    """Admin configuration for CaseNote model."""
    list_display = ['case', 'author', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['content', 'case__case_number']
