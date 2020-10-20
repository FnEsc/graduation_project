from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
import uuid
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from zanhu.notifications.views import notification_handler


@python_2_unicode_compatible
class News(models.Model):
    uuid_id = models.UUIDField(primary_key=True, verbose_name="id_news", default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name="publisher", verbose_name="user")
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="thread",
                               verbose_name="self_parent")
    content = models.TextField(verbose_name="news_content")
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_news", verbose_name="news_liked_user")
    reply = models.BooleanField(default=False, verbose_name="is_reply")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated_at")

    class Meta:
        verbose_name_plural = verbose_name = "home"
        ordering = ("-created_at",)

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        """重写save，适应通知功能"""
        super(News, self).save(*args, **kwargs)
        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                "type": "receive",
                "key": "additional_news",
                "actor_name": self.user.username,
            }
            async_to_sync(channel_layer.group_send)("notifications", payload)

    def switch_like(self, user):
        """点赞或取消赞"""
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)
            # 通知楼主
            notification_handler(user, self.user, "L", self, id_value=str(self.uuid_id), key="social_update")

    def get_parent(self):
        """返回自关联中的上级记录或本身"""
        return self.parent if bool(self.parent) == True else self
        # if self.parent:
        #         #     return self.parent
        #         # else:
        #         #     return self

    def reply_this(self, user_reply, text_reply):
        """
        回复首页的动态
        :param user_reply: 当前登录的用户
        :param text_reply: 回复的内容
		:return: None
        """
        parent_obj = self.get_parent()
        News.objects.create(
            # uuid_id =uuid.uuid4(),
            reply=True,
            user=user_reply,
            content=text_reply,
            parent=parent_obj
        )
        notification_handler(user_reply, parent_obj.user, "R", parent_obj, id_value=str(parent_obj.uuid_id), key="social_update")

    def get_thread(self):
        """关联到当前记录的所有记录"""
        parent = self.get_parent()
        return parent.thread.all()

    def comment_count(self):
        return self.get_thread().count()

    def count_likers(self):
        return self.liked.count()

    def get_likers(self):
        return self.liked.all()
