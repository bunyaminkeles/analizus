"""
ASGI config for analizdestek project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import forum.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analizdestek.settings')

# Standart HTTP istekleri için Django'nun kendi ASGI uygulamasını al
django_asgi_app = get_asgi_application()

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
