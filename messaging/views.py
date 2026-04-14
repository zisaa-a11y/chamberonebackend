from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationListCreateView(generics.ListCreateAPIView):
    """List user's conversations or start a new one."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        participant_id = request.data.get('participant_id')
        if not participant_id:
            return Response({'error': 'participant_id required'}, status=400)
        try:
            other = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        # Check if conversation already exists between these two
        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=other)
        if existing.exists():
            serializer = self.get_serializer(existing.first())
            return Response(serializer.data)

        conv = Conversation.objects.create()
        conv.participants.add(request.user, other)
        serializer = self.get_serializer(conv)
        return Response(serializer.data, status=201)


class ConversationDetailView(generics.RetrieveAPIView):
    """Get a single conversation."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class MessageListCreateView(generics.ListCreateAPIView):
    """List messages in a conversation or send a new one."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conv_id = self.kwargs['conversation_id']
        return Message.objects.filter(
            conversation_id=conv_id,
            conversation__participants=self.request.user,
        )

    def perform_create(self, serializer):
        conv_id = self.kwargs['conversation_id']
        conv = Conversation.objects.filter(
            id=conv_id, participants=self.request.user
        ).first()
        if not conv:
            raise permissions.PermissionDenied('Not a participant')
        serializer.save(sender=self.request.user, conversation=conv)
        conv.save()  # update updated_at


class MarkMessagesReadView(APIView):
    """Mark all messages in a conversation as read (except own)."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, conversation_id):
        count = Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=request.user,
            is_read=False,
        ).exclude(sender=request.user).update(is_read=True)
        return Response({'marked_read': count})
