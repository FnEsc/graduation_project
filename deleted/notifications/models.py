from __future__ import unicode_literals
import uuid

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import serializers

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify  # 用于生成url别名
from taggit.managers import TaggableManager
from collections import Counter


@python_2_unicode_compatible
class NotificationQuerySet(models.query.QuerySet):

    def unread(self):
        return self.filter(unread=True)

    def read(self):
        return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        """全部标记为已读"""
        qs = self.unread()
        if recipient:
            qs.filter(recipient=recipient)
        return qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        """全部标记为未读"""
        qs = self.read()
        if recipient:
            qs.filter(recipient=recipient)
        return qs.update(unread=True)

    def get_most_recent(self, recipient):
        """获取最近5条未读通知"""
        qs = self.unread()[:5]
        if recipient:
            qs = qs.filter(recipient=recipient)[:5]
        return qs

    def serialize_latest_notifications(self, recipient=None):
        """序列化最近5条未读通知"""
        qs = self.get_most_recent(recipient)
        notification_dic = serializers.serialize("json", qs)
        return notification_dic


@python_2_unicode_compatible
class Notification(models.Model):
    NOTIFICATION_TYPE = (
        ("L", "赞了"),
        ("C", "评论了"),
        ("A", "回答"),
        ("W", "接受了回答"),
        ("R", "回复了"),
        ("I", "登录"),
        ("O", "退出"),
    )

    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notify_actor", on_delete=models.CASCADE,
                              verbose_name="触发者")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=False, related_name="notification_recipient",
                                  on_delete=models.CASCADE, verbose_name="接收者")
    unread = models.BooleanField(default=True, db_index=True, verbose_name="未读")
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name="(URL)别名")
    verb = models.CharField(max_length=1, choices=NOTIFICATION_TYPE, verbose_name="通知类别")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="notify_action_object",
                                     on_delete=models.CASCADE)  # 当然，content_Type这里是关联外键的，需要在其他模型类中定义关联列
    object_id = models.CharField(max_length=255)  # 指的是其他模型类的主键id，所以该类需要兼容所有关联模型类的主键格式
    action_object = GenericForeignKey("content_type", "object_id")  # 这里两个参数均为默认的，前者是寻找"applabel:model"，后者寻找记录id。
    objects = NotificationQuerySet.as_manager()  # 关联该类的自定义查询集

    class Meta:
        verbose_name_plural = verbose_name_plural = "通知"
        ordering = ("-created_at",)

    def __str__(self):
        if self.action_object:
            return f"{self.actor} {self.get_verb_display()} {self.action_object}"
        return f"{self.actor}{self.get_verb_display()}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(f"{self.recipient} {self.uuid_id} {self.verb}")
            super(Notification, self).save()

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()
