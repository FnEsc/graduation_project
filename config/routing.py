from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator  # 防止websocket的csrf攻击
from channels.security.websocket import OriginValidator
# OriginValidator可以手动添加访问主机列表，AllowedHostsOriginValidator则能自动读取项目设定

from zanhu.messager.consumers import MessagesConsumer
from zanhu.notifications.consumers import NotificationsConsumer

# self.scope["type"] 获取协议类型
# self.scope["url_route"]["kwargs"]["username"] 获取url中关键字参数
# channels routing 是scope级别的，一个连接只能由一个consumer接收和处理
application = ProtocolTypeRouter({
    # 'http': views, # 普通的http请求不需要我们手动在这里添加，框架会自动加载
    # "websocket": consumer
    "websocket": AllowedHostsOriginValidator(  # channels远程主机允许，会读取项目的setting文件
        AuthMiddlewareStack(  # 认证系统
            URLRouter([  # url匹配
                path("ws/<str:username>/", MessagesConsumer),
                path("ws/notifications/", NotificationsConsumer),
            ])
        )
    )
})

# AuthMiddlewareStack用于websocket认证，继承了CookieMiddleware, SessionMiddleware, AuthMiddleware ，兼容Django认证系统
