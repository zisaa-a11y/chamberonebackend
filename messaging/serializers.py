from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'sender_role',
                  'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_name', 'sender_role', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.email

    def get_sender_role(self, obj):
        return getattr(obj.sender, 'role', 'client')


class ParticipantSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role']

    def get_name(self, obj):
        return obj.get_full_name() or obj.email


class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message', 'unread_count',
                  'created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {
                'content': msg.content,
                'sender': msg.sender.id,
                'sender_name': msg.sender.get_full_name() or msg.sender.email,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read,
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
