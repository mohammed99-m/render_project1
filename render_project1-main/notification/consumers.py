# core/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Notification(AsyncWebsocketConsumer):
    async def connect(self):
        #self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'notification_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'notification': notification,
        }))