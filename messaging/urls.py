from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message-list'),
    path('conversations/<int:conversation_id>/read/', views.MarkMessagesReadView.as_view(), name='mark-read'),
]
