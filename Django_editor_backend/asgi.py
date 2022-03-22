"""
ASGI config for Django_editor_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

import online_editor.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_editor_backend.settings')

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
  "websocket": AuthMiddlewareStack(
          URLRouter(
              online_editor.routing.websocket_urlpatterns
          )
      ),
})