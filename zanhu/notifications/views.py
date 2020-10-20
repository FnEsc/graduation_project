from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async

from django.urls import reverse_lazy  # reverse表示应用到url,resolve表示url到应用
from django.shortcuts import render, get_object_or_404, redirect
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
from zanhu.notifications.models import Notification


class NotificationUnreadListView(LoginRequiredMixin, ListView):
    """未读消息通知列表"""
    model = Notification
    context_object_name = "notification_list"
    template_name = "notifications/notification_list.html"

    def get_queryset(self):
        return self.request.user.notification_recipient.unread()  # 登录用户的反向查询Notification的unread集合


@login_required
def mark_all_as_read(request):
    """将所有同志标记为已读"""
    request.user.notification_recipient.mark_all_as_read()
    redirect_url = request.GET.get("next")
    messages.success(request, f"用户{request.user}的所有通知已标记为已读。")
    if redirect_url:
        return redirect(redirect_url)
    return redirect("notifications:unread")


@login_required
def mark_as_read(request, slug):
    """将某条通知标记为已读"""
    notification = get_object_or_404(Notification, slug=slug)
    notification.mark_as_read()
    redirect_url = request.GET.get("next")
    messages.success(request, f"用户{request.user}的该一条通知已标记为已读。")
    if redirect_url:
        return redirect(redirect_url)
    return redirect("notifications:unread")


@login_required
def get_latest_notifications(request):
    """最近的未读通知"""
    notifications = request.user.notification_recipient.get_most_recent(request.user)
    return render(request, "notifications/most_recent.html", {"notifications": notifications})


def notification_handler(actor, recipient, verb, action_object, **kwargs):
    """
    通知处理器
    :param actor:           request.user 对象
    :param recipient:       user Instance 接收者实例，可以是一个或者是多个接收者
    :param verb:            str 通知类别
    :param action_object:   Instance 动作对象的实例
    :param kwargs:          key, id_value等
    :return:                None
    """

    if actor.username != recipient.username and recipient.username == action_object.user.username:
        # 只通知通知对象的用户
        key = kwargs.get("key", default="notification")
        id_value = kwargs.get("id_value", None)
        # 记录通知内容
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object
        )

        channel_layer = get_channel_layer()
        payload = {
            "type": "receive",
            "key": key,
            "actor_name": actor.username,
            "id_value": id_value

        }
        async_to_sync(channel_layer.group_send)("notifications", payload)
