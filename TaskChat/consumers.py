import json

from channels.generic.websocket import WebsocketConsumer


class xChatConsumer(WebsocketConsumer):
    def connect(self):
        print('--->:' + str(self.channel_layer))

        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = '运维咖啡吧：' + text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class yChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'ops_coffee'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = '运维咖啡吧：' + event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        print(self.username)
        self.room_group_name = 'matrix'
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        username = self.username
        # login the user to this session.
        # await login(self.scope, user)
        # save the session (if the session backend does not access the db you can use `sync_to_async`)
        # await database_sync_to_async(self.scope["session"].save)()
        # print('self.user', self.user)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': username+': '+message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))