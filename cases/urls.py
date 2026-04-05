from django.urls import path
from .views import (
    CaseListCreateView,
    CaseDetailView,
    CaseDocumentListCreateView,
    CaseDocumentDetailView,
    CaseTimelineListCreateView,
    CaseTimelineDetailView,
    CaseNoteListCreateView,
    CaseNoteDetailView,
    CaseStatusUpdateView,
    CaseAssignLawyerView,
)

app_name = 'cases'

urlpatterns = [
    # Cases
    path('', CaseListCreateView.as_view(), name='case_list'),
    path('<int:pk>/', CaseDetailView.as_view(), name='case_detail'),
    path('<int:pk>/assign-lawyer/', CaseAssignLawyerView.as_view(), name='case_assign_lawyer'),
    path('<int:pk>/status/', CaseStatusUpdateView.as_view(), name='case_status'),
    
    # Documents
    path('<int:case_id>/documents/', CaseDocumentListCreateView.as_view(), name='case_documents'),
    path('documents/<int:pk>/', CaseDocumentDetailView.as_view(), name='document_detail'),
    
    # Timeline
    path('<int:case_id>/timeline/', CaseTimelineListCreateView.as_view(), name='case_timeline'),
    path('timeline/<int:pk>/', CaseTimelineDetailView.as_view(), name='timeline_detail'),
    
    # Notes
    path('<int:case_id>/notes/', CaseNoteListCreateView.as_view(), name='case_notes'),
    path('notes/<int:pk>/', CaseNoteDetailView.as_view(), name='note_detail'),
]
