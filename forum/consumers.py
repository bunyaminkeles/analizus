import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Anlık mesajlaşma için WebSocket Consumer
    İki kullanıcı arasında özel sohbet odası oluşturur
    """

    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # URL'den karşı tarafın username'ini al
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.other_user = await self.get_user(self.other_username)

        if not self.other_user:
            await self.close()
            return

        # Benzersiz oda adı oluştur (her iki kullanıcı için aynı)
        user_ids = sorted([self.user.id, self.other_user.id])
        self.room_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        # Odaya katıl
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """Kullanıcıdan mesaj alındığında"""
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        attachment_url = data.get('attachment_url', '')
        attachment_name = data.get('attachment_name', '')

        if not message_text and not attachment_url:
            return

        # Mesajı veritabanına kaydet
        # Signal otomatik olarak hem bildirimi hem de chat mesajını gönderecek
        await self.save_message(message_text, attachment_url, attachment_name)

    async def chat_message(self, event):
        """Odadan mesaj geldiğinde tarayıcıya gönder"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'attachment_url': event.get('attachment_url', ''),
            'attachment_name': event.get('attachment_name', ''),
            'attachment_type': event.get('attachment_type', ''),
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
            'is_own': event['sender_id'] == self.user.id,
        }))

    @database_sync_to_async
    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, message_text, attachment_url='', attachment_name=''):
        from .models import PrivateMessage

        msg = PrivateMessage.objects.create(
            sender=self.user,
            receiver=self.other_user,
            message=message_text,
            attachment_name=attachment_name,
        )

        # Attachment type belirleme
        attachment_type = ''
        if attachment_name:
            ext = attachment_name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                attachment_type = 'image'
            elif ext == 'pdf':
                attachment_type = 'pdf'
            elif ext in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
                attachment_type = 'document'
            else:
                attachment_type = 'other'

        return {
            'id': msg.id,
            'timestamp': msg.created_at.strftime('%H:%M'),
            'attachment_type': attachment_type,
        }

    @database_sync_to_async
    def send_notification_to_receiver(self):
        """Karşı tarafa bildirim gönder"""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        notification_group = f'notifications_{self.other_user.id}'

        async_to_sync(channel_layer.group_send)(
            notification_group,
            {
                'type': 'notification_message',
                'message': f'<b>{self.user.username}</b> size yeni bir mesaj gönderdi.',
                'url': f'/messages/{self.user.username}/',
            }
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Kullanıcı WebSocket'e bağlandığında çağrılır.
        Kullanıcıyı doğrular ve ona özel bir gruba ekler.
        """
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        await self.accept()
        self.user_group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        print(f"--- DEBUG: Kullanıcı '{self.user.username}' bağlandı ve '{self.user_group_name}' grubuna eklendi. ---") # HATA AYIKLAMA

    async def disconnect(self, close_code):
        """
        Kullanıcının bağlantısı kesildiğinde çağrılır.
        Kullanıcıyı grubundan çıkarır.
        """
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def notification_message(self, event):
        """
        Gruptan bir bildirim mesajı aldığında bu metot çağrılır.
        Mesajı WebSocket üzerinden client'a (kullanıcının tarayıcısına) gönderir.
        """
        print(f"--- DEBUG: '{self.user_group_name}' grubundaki consumer mesaj aldı. Tarayıcıya gönderiliyor... ---")
        message = event['message']
        url = event.get('url', '#')

        await self.send(text_data=json.dumps({
            'message': message,
            'url': url
        }))
