from channels.layers import get_channel_layer  # 这里不需要再引入，因为在AsyncWwebsocketConsumer会引入
from channels.generic.websocket import AsyncWebsocketConsumer

import json

class MessagesConsumer(AsyncWebsocketConsumer):
    """处理私信应用中websocket请求"""

    async def connect(self):
        if self.scope["user"].is_anonymous:
            # 未登陆用户拒绝连接
            await self.close()
        else:
            # 加入聊天组
            await self.channel_layer.group_add(self.scope["user"].username, self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """离开聊天组"""
        await self.channel_layer.group_discard(self.scope["user"].username, self.channel_name)
