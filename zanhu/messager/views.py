from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async

from django.urls import reverse_lazy  # reverse表示应用到url,resolve表示url到应用
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required  # 这个是装饰器，可用于无类的函数view
from django.contrib.auth.mixins import LoginRequiredMixin  # 这个是继承类
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, ListView, DeleteView, DetailView
from django.contrib.auth import get_user_model
from django.conf import settings
from django.template.loader import render_to_string

from channels.layers import get_channel_layer

from zanhu.helpers import ajax_required
from zanhu.messager.models import Message


class MessagesListView(LoginRequiredMixin, ListView):
    """消息列表"""
    model = Message
    template_name = "messager/message_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesListView, self).get_context_data()

        # 获取除当前登录用户外的所有用户，按最近登录时间降序排列，相当于“好友列表”，但是全部用户都是好友关系
        context["users_list"] = get_user_model().objects.filter(is_active=True).exclude(
            username=self.request.user).order_by("-last_login")[:10]

        # 获取最近一次私信互动的用户
        last_conversation = Message.objects.get_recentest_conversation(self.request.user)
        context["active"] = last_conversation.username

        return context

    def get_queryset(self):
        """最近一个用户的私信互动的内容"""
        actice_user = Message.objects.get_recentest_conversation(self.request.user)
        return Message.objects.get_conversation(actice_user, self.request.user)


class MessagesConversationListView(MessagesListView):
    """获取与指定用户的私信内容"""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesConversationListView, self).get_context_data()
        context["active"] = self.kwargs["username"]  # context["active"]表示当前聊天框的用户名
        return context

    def get_queryset(self):
        active_user = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        return Message.objects.get_conversation(active_user, self.request.user)


@login_required
@ajax_required
@require_http_methods(["POST"])
def send_message(request):
    """发送消息，ajax post请求"""
    sender = request.user
    recipient_username = request.POST["to"]
    # recipient = settings.AUTH_USER_MODEL.object.get(username=recipient_username)
    recipient = get_user_model().objects.get(username=recipient_username)  # 与上面语句等价
    message = request.POST["message"]
    if len(message.strip()) != 0 and sender != recipient:  # 消息不为空并且不是发给自己
        msg = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            message=message
        )

        channel_layer = get_channel_layer()
        payload = {
            "type": "receive",  # 这两个字段是固定的，代表执行consumer.py的receive函数
            "message": render_to_string("messager/single_message.html", {"message": msg}),  # 这里是返回前端的html代码
            "sender": sender.username
        }
        # 把异步变同步：channel_layer.group_send(recipient_username, payload)
        async_to_sync(channel_layer.group_send)(recipient_username, payload)

        return render(request, "messager/single_message.html", {"message": msg})
    return HttpResponse()

# 这里不使用ajax前端get请求刷新receive_message，使用websocket

