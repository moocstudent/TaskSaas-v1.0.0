from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from TaskChat.consumers import yChatConsumer, CacheChatConsumer

websocket_urlpatterns = [
    path('chat/ws/<str:project_id>/<str:user_id>/<str:username>', yChatConsumer.as_asgi()),
    path('cache_chat/ws/<str:project_id>/<str:user_id>/<str:username>', CacheChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})