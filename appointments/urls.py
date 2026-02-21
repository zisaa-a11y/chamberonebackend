from django.urls import path
from .views import (
    AppointmentListCreateView,
    AppointmentDetailView,
    AppointmentStatusUpdateView,
    UpcomingAppointmentsView,
    LawyerAppointmentsView,
)

app_name = 'appointments'

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment_list'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/status/', AppointmentStatusUpdateView.as_view(), name='appointment_status'),
    path('upcoming/', UpcomingAppointmentsView.as_view(), name='upcoming_appointments'),
    path('lawyer/<int:lawyer_id>/', LawyerAppointmentsView.as_view(), name='lawyer_appointments'),
]
