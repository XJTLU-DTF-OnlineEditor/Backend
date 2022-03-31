import json
from channels.generic.websocket import AsyncWebsocketConsumer
from online_editor.core import input_in


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.code_id = None

    # Web socket 链接之后
    async def connect(self):
        self.code_id = self.scope['url_route']['kwargs']['code_id']  # code ID 作为链接的名字

        await self.channel_layer.group_add(
            self.code_id,
            self.channel_name
        )

        await self.accept()

    # 链接断开后
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.code_id,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        print("【INPUT】", text_data)
        input_in(self.code_id, text_data)

    # Receive message from room group
    async def chat_message(self, event):
        data = event['data']
        print("【OUTPUT】", data)
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))