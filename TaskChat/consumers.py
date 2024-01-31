import datetime
import json
import re
from bs4 import BeautifulSoup

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.http import JsonResponse

from TaskChat import constants
from TaskChat.constants import private_message_key, push_message_key, userlist_message_key, chat_message_key
from TaskSaasAPP import date_util
from TaskSaasAPP.hash_map_util import HashMap
from utils import encrypt
from web import models
from web.models import InfoLog


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


from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer

users = set()


hash_map = HashMap()


class yChatConsumer(WebsocketConsumer):
    def connect(self):
        print('yChat connect')
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.room_group_name = 'matrix' + self.project_id
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        # self.position = self.scope["url_route"]["kwargs"]["position"]
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        print('self.room_group_name', self.room_group_name)
        async_to_sync(self.channel_layer.group_add)(
            encrypt.md5(self.username) +'__'+ self.project_id,
            self.channel_name
        )

        self.accept()
        the_room_users = hash_map.get(self.room_group_name)
        if the_room_users and the_room_users.val:
            print('the_room', the_room_users)
            room_users = the_room_users.val
            room_users.add(self.username)
            hash_map._put(self.room_group_name, room_users)
            print('connect users this room ', list(hash_map.get(self.room_group_name).val))
        else:
            room_users = set()
            room_users.add(self.username)
            hash_map._put(self.room_group_name,room_users)
            print('connect users this room ', list(hash_map.get(self.room_group_name).val))
        push_message_to_group(self.room_group_name,userlist_reset(self.project_id) , userlist_message_key)

        # 提示消息
        # push_message_to_group(self.username,'欢迎来到该项目组聊天室,'+self.username,private_message_key)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )
        async_to_sync(self.channel_layer.group_discard)(
            encrypt.md5(self.username) + '__' + self.project_id,
            self.channel_name
        )
        the_room_users = hash_map.get(self.room_group_name)
        if the_room_users and the_room_users.val:
            print('the_room', the_room_users)
            room_users = the_room_users.val
            room_users.discard(self.username)
            hash_map._put(self.room_group_name,room_users)
            print('connect users this room ', list(hash_map.get(self.room_group_name).val))
        else:
            print('disconnect users this room ', None)
            pass
        push_message_to_group(self.room_group_name, userlist_reset(self.project_id), userlist_message_key)

        # push_message_to_group(self.room_group_name,self.username+' <已离线>')

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        print('msg type',type)
        message = text_data_json['message']
        username = self.username

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': chat_message_key,
                'message': username + ': ' + message,
            }
        )

        if type == 'hint':
            receivers = text_data_json['receivers']
            sender = text_data_json['sender']
            print('hint msg receivers ',receivers)
            for receiver in receivers:
                print('push hint msg to ',receiver)
                push_message_to_group(encrypt.md5(receiver)+'__'+str(self.project_id),message,constants.private_message_key,sender)

    # Receive message from room group
    def chat_message(self, event):
        message = date_util.get_today_until_second() + '>> ' + event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': chat_message_key
        }))

    # 消息推送
    def push_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        message = '❗️系统消息❗️' + event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': type
        }))
        save_msg_to_db_impl(message,'admin', None,1,self.project_id)

    def private_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        sender = event['sender']
        print('sender: ',sender)
        message = '😄来自'+sender+'的私人消息😄' + event['message']
        type = event['type']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': type
        }))
        print('private_message self.room_group_name ',self.room_group_name)
        save_msg_to_db_impl(message,sender,username,2,self.project_id)


    def userlist_message(self, event):
        username = self.username
        message = event['message']
        type = event['type']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': type
        }))


from channels.generic.websocket import AsyncWebsocketConsumer


class CacheChatConsumer(WebsocketConsumer):
    def connect(self):
        print('CacheChat connect')
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.room_group_name = 'matrix' + self.project_id
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        # self.position = self.scope["url_route"]["kwargs"]["position"]
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        print('self.room_group_name', self.room_group_name)
        async_to_sync(self.channel_layer.group_add)(
            encrypt.md5(self.username) +'__'+ self.project_id,
            self.channel_name
        )

        self.accept()
        the_room_users = hash_map.get(self.room_group_name)
        if the_room_users and the_room_users.val:
            print('the_room', the_room_users)
            room_users = the_room_users.val
            room_users.add(self.username)
            hash_map._put(self.room_group_name, room_users)
            print('connect users this room ', list(hash_map.get(self.room_group_name).val))
        else:
            room_users = set()
            room_users.add(self.username)
            hash_map._put(self.room_group_name,room_users)
            print('connect users this room ', list(hash_map.get(self.room_group_name).val))
        push_message_to_group(self.room_group_name,userlist_reset(self.project_id) , userlist_message_key)

        # 提示消息
        # push_message_to_group(self.username,'欢迎来到该项目组聊天室,'+self.username,private_message_key)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )
        async_to_sync(self.channel_layer.group_discard)(
            encrypt.md5(self.username) + '__' + self.project_id,
            self.channel_name
        )
        the_room_users = hash_map.get(self.room_group_name)
        if the_room_users and the_room_users.val:
            print('the_room', the_room_users)
            room_users = the_room_users.val
            room_users.discard(self.username)
            hash_map._put(self.room_group_name,room_users)
            print('connect users this room ', list(hash_map.get(self.room_group_name).val))
        else:
            print('disconnect users this room ', None)
            pass
        push_message_to_group(self.room_group_name, userlist_reset(self.project_id), userlist_message_key)

        # push_message_to_group(self.room_group_name,self.username+' <已离线>')

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        print('msg type',type)
        message = text_data_json['message']
        username = self.username

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': chat_message_key,
                'message': username + ': ' + message,
            }
        )

        if type == 'hint':
            receivers = text_data_json['receivers']
            sender = text_data_json['sender']
            print('hint msg receivers ',receivers)
            for receiver in receivers:
                print('push hint msg to ',receiver)
                push_message_to_group(encrypt.md5(receiver)+'__'+str(self.project_id),message,constants.private_message_key,sender)

    # Receive message from room group
    def chat_message(self, event):
        message = date_util.get_today_until_second() + '>> ' + event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': chat_message_key
        }))

    # 消息推送
    def push_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        message = '❗️系统消息❗️' + event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': type
        }))
        save_msg_to_db_impl(message,'admin', None,1,self.project_id)

    def private_message(self, event):
        # user = await get_user(self.scope)
        username = self.username
        sender = event['sender']
        print('sender: ',sender)
        message = '😄来自'+sender+'的私人消息😄' + event['message']
        type = event['type']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': type
        }))
        print('private_message self.room_group_name ',self.room_group_name)
        save_msg_to_db_impl(message,sender,username,2,self.project_id)


    def userlist_message(self, event):
        username = self.username
        message = event['message']
        type = event['type']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'type': type
        }))


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print('Chat connect')
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        # print(self.username)
        self.room_group_name = 'matrix' + self.project_id
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

def push_message_to_group(group_name, message, type=None,sender=None):
    channel_layer = get_channel_layer()
    if type is None:
        type = push_message_key
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": type,
            "message": message,
            'sender': sender
        }
    )


pattern = r'<a\s+href="([^"]*)">(.*?)</a>'

def save_msg_to_db_impl(msg,sender,receiver,type,project_id):
    print('save_msg_to_db_impl')
    user = models.UserInfo.objects.filter(username=sender).first()
    receiver_ = models.UserInfo.objects.filter(username=receiver).first()
    project = models.Project.objects.filter(id=project_id).first()
    pure_content = None
    pure_link = None
    if msg.__contains__('<a'):
        print('contains a',msg)
        # 使用正则表达式提取a标签的链接和文本内容
        for link,text in extract_links_and_text(msg):
            print(link)
            pure_link=link
            print(text)
            pure_content=text

    info_log = InfoLog(content=msg,sender=user,receiver=receiver_,type=type,project_id=project,
                       pure_link=pure_link,pure_content=pure_content)
    info_log.save()



def extract_links_and_text(text):
    # 使用正则表达式提取a标签
    pattern = r'<a\s+href=[\'"]?([^\'" >]+)[\'"]?[^>]*>(.*?)<\/a>'
    matches = re.findall(pattern, text)

    # 使用BeautifulSoup解析a标签内容
    soup = BeautifulSoup(text, 'html.parser')
    links_and_text = []

    for match in matches:
        link = match[0]
        # 解析a标签内容，去除HTML标签
        soup_link = BeautifulSoup(match[1], 'html.parser')
        text = soup_link.get_text()
        links_and_text.append((link, text))

    return links_and_text



def send_private_hint_msg(request,project_id):
    print('send_private_hint_msg')
    try:
        sender = request.web.user.username
        receiver = request.POST.get("receiver")
        message = request.POST.get("message")
        if message:
            message = ('来自'+sender+'的回复信息:')+message
        save_msg_to_db_impl(message,request.web.user.username,receiver,2,project_id)
        #fixme The receiver maybe not connection
        push_message_to_group(encrypt.md5(receiver) + '__' + str(project_id), message, constants.private_message_key,
                              request.web.user.username)
    except:
        return JsonResponse({'status':0})
    return JsonResponse({'status': 1})

status_hash_map = HashMap()
status_hash_map._put('peeropen','视频会议中')
status_hash_map._put('peerclose','')

peer_id_map = HashMap()

on_peer_user_list = []

def received_userlist_status(request,project_id):
    print('received_userlist_status')
    status = request.POST.get('status')
    print('status ',status)
    peer_id = request.POST.get('peer_id')
    peer_id_map._put(request.web.user.username,peer_id)
    userlist = list(hash_map.get('matrix' + project_id).val)
    if status:
        print('userlist:',userlist)
        if (status == 'peeropen'):
            print('peeropen')
            on_peer_user_list.append(request.web.user.username)
        elif (status=='peerclose'):
            print('peerclose')
            on_peer_user_list.remove(request.web.user.username)
        print('on_peer_user_list ',on_peer_user_list)
        push_message_to_group('matrix' + project_id,userlist_reset(project_id), userlist_message_key)
        return JsonResponse({'status': 1})
    return JsonResponse({'status': 0})

def userlist_reset(project_id):
    userlist=list(hash_map.get('matrix' + project_id).val)
    userlist_ = []
    for u in userlist:
        uname = u.split(' ')[0]
        print('u', uname)
        if uname in on_peer_user_list:
            print('eq user')
            uname += ' ' + str(status_hash_map.get('peeropen'))
            userlist_.append(uname)
        else:
            userlist_.append(uname)
    return (userlist_)
