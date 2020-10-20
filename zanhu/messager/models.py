from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.auth import get_user_model

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify  # 用于生成url别名
from taggit.managers import TaggableManager

import uuid
from collections import Counter


class MessageQuerySet(models.query.QuerySet):

    def get_conversation(self, sender, recipient):
        """私信记录"""
        qs_one = self.filter(sender=sender, recipient=recipient)
        qs_two = self.filter(sender=recipient, recipient=sender)
        return qs_one.union(qs_two).order_by("created_at")

    def get_recentest_conversation(self, user):
        """
        :argument user为当前登录用户object
        返回当前登录用户最近一次私信互动的用户
        """
        try:
            qs_sent = self.filter(sender=user) # 当前登录用户发送的消息
            qs_recived = self.filter(recipient=user) # 当前登录用户接收的消息
            qs = qs_sent.union(qs_recived).latest("created_at") # 合并后获取最近时间的最后一条消息

            # qs为最后一条消息，返回另一方
            return qs.sender if qs.recipient==user else qs.recipient
        except self.model.DoesNotExist:
            # 假如没有任何消息，会在latest()中出错
            return get_user_model().objects.get(username=user.username)

@python_2_unicode_compatible
class Message(models.Model):
    """用户间私信"""
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages", blank=True, null=True,
                               on_delete=models.SET_NULL, verbose_name="发送者")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_messages", blank=True, null=True,
                               on_delete=models.SET_NULL, verbose_name="接收者")
    message = models.TextField(blank=True, null=True, verbose_name="私信内容")
    unread = models.BooleanField(default=True, db_index=True, verbose_name="是否未读")
    created_at =models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    objects = MessageQuerySet.as_manager()  # 关联该类的自定义查询集

    class Meta:
        verbose_name_plural = verbose_name = "私信"
        ordering = ("-created_at",)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()
