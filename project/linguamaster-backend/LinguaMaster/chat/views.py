from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from django.utils import timezone

from .models import Conversation, Message
from .serializers import (ConversationSerializer, MessageSerializer,
                         CreateConversationSerializer)

class ConversationViewSet(ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).order_by('-last_message_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request):
        serializer = CreateConversationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        participant_ids = serializer.validated_data['participant_ids']
        is_group = serializer.validated_data['is_group']
        group_name = serializer.validated_data.get('group_name', '')
        
        participants = [request.user]
        for participant_id in participant_ids:
            from users.models import User
            try:
                user = User.objects.get(id=participant_id)
                participants.append(user)
            except User.DoesNotExist:
                pass
        
        conversation = Conversation.objects.create(
            is_group=is_group,
            group_name=group_name if is_group else None
        )
        conversation.participants.set(participants)
        conversation.save()
        
        return Response(ConversationSerializer(conversation, context={'request': request}).data,
                       status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('created_at')
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        content = request.data.get('content', '').strip()
        message_type = request.data.get('message_type', 'text')
        media_url = request.data.get('media_url', None)
        
        if not content and not media_url:
            return Response({'error': 'Content or media required'},
                           status=status.HTTP_400_BAD_REQUEST)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            message_type=message_type,
            media_url=media_url
        )
        
        conversation.last_message = content
        conversation.last_message_at = timezone.now()
        conversation.save()
        
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'success': True})

class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return Message.objects.filter(
                conversation_id=conversation_id,
                conversation__participants=self.request.user
            ).order_by('created_at')
        return Message.objects.none()