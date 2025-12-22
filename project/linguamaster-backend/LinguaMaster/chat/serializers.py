from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'message_type',
                 'media_url', 'media_size', 'is_read', 'read_at', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message_detail = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'is_group', 'group_name', 'group_image',
                 'last_message', 'last_message_at', 'created_at', 'updated_at',
                 'last_message_detail', 'unread_count']
    
    def get_last_message_detail(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100],
                'sender': last_message.sender.username,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class CreateConversationSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    is_group = serializers.BooleanField(default=False)
    group_name = serializers.CharField(required=False, allow_blank=True)