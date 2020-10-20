from channels.layers import get_channel_layer  # 这里不需要再引入，因为在AsyncWwebsocketConsumer会引入
from channels.generic.websocket import AsyncWebsocketConsumer

import json
