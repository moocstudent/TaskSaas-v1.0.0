from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from TaskChat.consumers import xChatConsumer, ChatConsumer

websocket_urlpatterns = [
    path('chat/ws/<str:user_id>/<str:username>', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})