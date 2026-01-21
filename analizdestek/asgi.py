"""
ASGI config for analizdestek project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Django'nun ayarları diğer importlardan ÖNCE yapılandırılmalı.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analizdestek.settings')

# Django'nun temel ASGI uygulamasını erkenden yükleyerek ayarların
# ve uygulama kayıt defterinin (app registry) hazır olmasını sağla.
django_asgi_app = get_asgi_application()

# Django ayarları artık hazır olduğuna göre, modellere veya ayarlara
# ihtiyaç duyan diğer Channels bileşenlerini import edebiliriz.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import forum.routing

application = ProtocolTypeRouter({
    # HTTP istekleri Django'ya yönlendirilir
    "http": django_asgi_app,

    # WebSocket bağlantıları AuthMiddlewareStack ile sarmalanarak 
    # kimlik doğrulama bilgilerine erişim sağlar ve URLRouter'a yönlendirilir.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            forum.routing.websocket_urlpatterns
        )
    ),
})
