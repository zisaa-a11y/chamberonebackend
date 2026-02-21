from django.urls import path
from .views import (
    PracticeAreaListCreateView,
    PracticeAreaDetailView,
    LawyerListView,
    LawyerDetailView,
    LawyerProfileUpdateView,
    LawyersByPracticeAreaView,
    LawyerAvailabilityListCreateView,
    LawyerAvailabilityDetailView,
    PublicLawyerAvailabilityView,
)

app_name = 'lawyers'

urlpatterns = [
    # Practice Areas
    path('practice-areas/', PracticeAreaListCreateView.as_view(), name='practice_area_list'),
    path('practice-areas/<int:pk>/', PracticeAreaDetailView.as_view(), name='practice_area_detail'),
    
    # Lawyers
    path('', LawyerListView.as_view(), name='lawyer_list'),
    path('<int:pk>/', LawyerDetailView.as_view(), name='lawyer_detail'),
    path('profile/', LawyerProfileUpdateView.as_view(), name='lawyer_profile'),
    path('by-practice-area/<int:practice_area_id>/', LawyersByPracticeAreaView.as_view(), name='lawyers_by_practice_area'),
    
    # Availability
    path('availability/', LawyerAvailabilityListCreateView.as_view(), name='availability_list'),
    path('availability/<int:pk>/', LawyerAvailabilityDetailView.as_view(), name='availability_detail'),
    path('<int:lawyer_id>/availability/', PublicLawyerAvailabilityView.as_view(), name='public_availability'),
]
