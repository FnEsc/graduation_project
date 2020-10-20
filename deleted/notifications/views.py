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
from zanhu.notifications.models import Notification

class NotificationUnreadListView(LoginRequiredMixin, ListView):
    """未读消息通知列表"""
    model = Notification
    context_object_name = "notification_list"
    template_name = "notifications/notifications_list.html"

    def get_queryset(self):
        return self.request.user.notification_recipient.unread() # 登录用户的反向查询Notification的unread集合

@login_required
def get_latest_notifications(request):
    """最近的未读通知"""
    notifications = request.user.notification_recipient.get_most_recent(request.user)
    return render(request, "notifications/most_recent.html", {"notifications": notifications})

