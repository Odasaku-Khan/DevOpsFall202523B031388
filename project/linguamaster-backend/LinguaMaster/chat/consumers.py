import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.send_online_status(True)
    
    async def disconnect(self, close_code):
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
        
        await self.send_online_status(False)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            content = data.get('content', '').strip()
            message_type = data.get('message_type', 'text')
            media_url = data.get('media_url', None)
            
            if content or media_url:
                message = await self.save_message(content, message_type, media_url)
                
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': str(message.id),
                            'sender': {
                                'id': str(self.user.id),
                                'username': self.user.username,
                                'avatar_url': self.user.avatar_url
                            },
                            'content': message.content,
                            'message_type': message.message_type,
                            'media_url': message.media_url,
                            'created_at': message.created_at.isoformat()
                        }
                    }
                )
        
        elif message_type == 'typing':
            is_typing = data.get('is_typing', False)
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'typing_indicator',
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username
                    },
                    'is_typing': is_typing
                }
            )
        
        elif message_type == 'read_receipt':
            message_id = data.get('message_id')
            await self.mark_message_read(message_id)
            
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username
                    }
                }
            )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))
    
    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user': event['user']
        }))
    
    async def send_online_status(self, is_online):
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'online_status',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username
                },
                'is_online': is_online
            }
        )
    
    async def online_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_status',
            'user': event['user'],
            'is_online': event['is_online']
        }))
    
    @database_sync_to_async
    def save_message(self, content, message_type, media_url):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
            message_type=message_type,
            media_url=media_url
        )
        
        conversation.last_message = content
        conversation.save()
        
        return message
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if not message.is_read and message.sender != self.user:
                message.is_read = True
                message.save()
        except Message.DoesNotExist:
            pass