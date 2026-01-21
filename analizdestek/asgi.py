"""
ASGI config for analizdestek project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Django'nun ayarları diğer importlardan ÖNCE yapılandırılmalı.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analizdestek.settings')

# Ayarların tam olarak yüklendiğinden ve uygulama kayıt defterinin
# hazır olduğundan emin olmak için django.setup() komutunu manuel olarak çağır.
# Bu, bazı canlı sunucu ortamlarında ortaya çıkan "race condition" hatalarını önler.
django.setup()

# Django ayarları artık hazır olduğuna göre, modellere veya ayarlara
# ihtiyaç duyan diğer Channels bileşenlerini import edebiliriz.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import forum.routing

application = ProtocolTypeRouter({
    # HTTP istekleri Django'ya yönlendirilir
    "http": get_asgi_application(),

    # WebSocket bağlantıları AuthMiddlewareStack ile sarmalanarak 
    # kimlik doğrulama bilgilerine erişim sağlar ve URLRouter'a yönlendirilir.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            forum.routing.websocket_urlpatterns
        )
    ),
})
