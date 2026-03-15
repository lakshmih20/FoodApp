"""
ASGI config for homefood project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homefood.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from channels.auth import AuthMiddleware
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from apps.live_streaming.routing import websocket_urlpatterns as live_stream_websocket_urlpatterns
from apps.notifications.routing import websocket_urlpatterns as notification_websocket_urlpatterns

# SessionMiddlewareStack loads session first, then AuthMiddleware gets user from it.
# This ensures the cook (and all users) are authenticated for WebSocket chat.
application = ASGIStaticFilesHandler(
	ProtocolTypeRouter(
		{
			'http': django_asgi_app,
			'websocket': SessionMiddlewareStack(
				AuthMiddleware(
					URLRouter(notification_websocket_urlpatterns + live_stream_websocket_urlpatterns)
				)
			),
		}
	)
)






