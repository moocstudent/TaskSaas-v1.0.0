import datetime
import json

from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.http import JsonResponse

from TaskSaasAPP import date_util


class xChatConsumer(WebsocketConsumer):
    def connect(self):
        print('--->:' + str(self.channel_layer))

        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = '：' + text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class yChatConsumer(WebsocketConsumer):
    def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.room_group_name = 'matrix'+self.project_id
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.accept()

        # push_message_to_group(self.room_group_name,self.username+' <已上线>')

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )
        # push_message_to_group(self.room_group_name,self.username+' <已离线>')

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.username

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': username+': '+ message
            }
        )
        # push(self.room_group_name,'system info')
        # async_to_sync(system_info_push(self))

    # Receive message from room group
    def chat_message(self, event):
        message = date_util.get_today_until_second()+'>> ' + event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
    # 消息推送
    def push_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        message = '❗️系统消息❗️'+event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        # print(self.username)
        self.room_group_name = 'matrix'+self.project_id
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
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'push_message',
        #         'message' :'😄system_info😄 : '+ +message
        #     }
        # )

    # Receive message from room group
    async def push_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

# class PushConsumer(AsyncWebsocketConsumer):
#   async def connect(self):
#     self.group_name = self.scope['url_route']['kwargs']['username']
#     await self.channel_layer.group_add(
#       self.group_name,
#       self.channel_name
#     )
#     await self.accept()
#   async def disconnect(self, close_code):
#     await self.channel_layer.group_discard(
#       self.group_name,
#       self.channel_name
#     )
#     # print(PushConsumer.chats)
#   async def push_message(self, event):
#     print(event)
#     await self.send(text_data=json.dumps({
#       "event": event['event']
#     }))

def push_message_to_group(group_name, message):
  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.group_send)(
    group_name,
    {
      "type": "push.message",
      "message": message
    }
  )