# forum/routing.py
from django.urls import re_path

from .consumers import NotificationConsumer, ChatConsumer

# Gelen WebSocket bağlantılarını consumer'lara yönlendiren URL listesi
websocket_urlpatterns = [
    # Bildirimler için WebSocket
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),

    # Anlık mesajlaşma için WebSocket
    re_path(r'ws/chat/(?P<username>\w+)/$', ChatConsumer.as_asgi()),
]
