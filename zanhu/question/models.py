from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify  # 用于生成url别名
from taggit.managers import TaggableManager

import uuid
from collections import Counter


@python_2_unicode_compatible
class Vote(models.Model):
    """使用Django中的ConetntType，同时关联用户对问题和回答的投票"""
    uuid_id = models.UUIDField(primary_key=True, verbose_name="id_vote", default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vote_user",
                             verbose_name="投票用户")
    value = models.BooleanField(default=True, verbose_name="赞同或反对")  # True赞同，False反对
    # GenericForeignKey设置
    content_type = models.ForeignKey(ContentType, related_name="vote_on",
                                     on_delete=models.CASCADE)  # 当然，content_Type这里是关联外键的，需要在其他模型类中定义关联列
    object_id = models.CharField(max_length=255)  # 指的是其他模型类的主键id，所以该类需要兼容所有关联模型类的主键格式
    vote = GenericForeignKey("content_type", "object_id")  # 这里两个参数均为默认的，前者是寻找"applabel:model"，后者寻找记录id。
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name_plural = verbose_name = "投票"
        unique_together = ("user", "content_type", "object_id")  # 设置联合唯一主键
        index_together = ("content_type", "object_id")  # SQL优化：设置联合唯一索引


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):
    """自定义QuerySet，提高模型类的可用性"""

    def get_answered(self):
        """获取已有最佳回答的问题"""
        return self.filter(has_answer=True)

    def get_unanswered(self):
        """获取未有最佳回答的问题"""
        return self.filter(has_answer=False)

    def get_counted_tags(self):
        """统计所有问题标签的数量（大于0的）"""
        tag_dict = {}
        query = self.all()  # 因为贴上标签的都会大于0而返回，不需要再过滤再大于0 .annotate(tagged=models.Count("tags")).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


# Create your models here.
@python_2_unicode_compatible
class Question(models.Model):
    STATUS = (("D", "Draft"), ("O", "Open"), ("C", "Close"))

    title = models.CharField(max_length=255, unique=True, verbose_name="问题标题")  # verbose_name不是sql的注释，这里是作为python查询的别名
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, on_delete=models.CASCADE,
                             related_name="question_author", verbose_name="问题提问者")
    slug = models.SlugField(max_length=255, verbose_name="question_(URL)别名")  # 主流浏览器url至少支持2083个字符
    status = models.CharField(max_length=1, choices=STATUS, default="O", verbose_name="问题状态")
    content = MarkdownxField(verbose_name="问题内容")
    has_answer = models.BooleanField(default=False, verbose_name="是否已接受最佳答案")
    vote = GenericRelation(Vote, verbose_name="投票情况")  # 通过GenericRelation关联到Vote表，非实际字段，只是外键关联表字段
    tags = TaggableManager(help_text="多个标签使用,(英文)隔开", verbose_name="标签")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = QuestionQuerySet.as_manager()  # 关联该类的自定义查询集

    class Meta:
        verbose_name_plural = verbose_name = "问题"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save()  # python2的写法是：super().save()

    def get_markdown(self):
        """将markdown文本渲染成html"""
        return markdownify(self.content)  # 由markdown调用，返回markdwon的Html代码

    def total_votes(self):
        """得票数"""
        dic = Counter(self.vote.values_list("value", flat=True))  # 分别统计赞同、反对票数
        # 上面vote为Question的vote外键表类，value为外键表类的布尔类型字段，flat参数表示传递单个值，返回结果也为单个值而不是一个元组
        # 等价于 ： dic = Counter(Vote.objects.values_list("value",flat=True)) # 分别统计赞同、反对票数
        return dic[True] - dic[False]

    def get_answers(self):
        return Answer.objects.filter(question=self)  # 当前问题的回答

    def count_answers(self):
        return self.get_answers().count()  # 统计当前问题回答的数量

    def get_upvoters(self):
        """赞同的用户"""
        return [vote.user for vote in self.vote.filter(value=True)]

    def get_downvoters(self):
        """反对的用户"""
        return [vote.user for vote in self.vote.filter(value=False)]

    def get_accpetd_answer(self):
        """获取最佳答案"""
        return Answer.objects.get(question=self, is_answer=True)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, verbose_name="id_answer", default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="answer_author", on_delete=models.CASCADE,
                             verbose_name="回答者")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="回答关联的问题")
    content = MarkdownxField(verbose_name="回答内容")
    is_answer = models.BooleanField(default=False, verbose_name="回答是否被采纳")
    vote = GenericRelation(Vote, verbose_name="投票情况")  # 通过GenericRelation关联到Vote表，非实际字段，只是外键关联表字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ("-is_answer", "-created_at")  # 采纳答案、最新排序
        verbose_name_plural = verbose_name = "回答"  # plural复数的

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """得票数"""
        dic = Counter(self.vote.values_list("value", flat=True))  # 分别统计赞同、反对票数
        # 上面vote为Question的vote外键表类，value为外键表类的布尔类型字段，flat参数表示传递单个值，返回结果也为单个值而不是一个元组
        # 等价于 ： dic = Counter(Vote.objects.values_list("value",flat=True)) # 分别统计赞同、反对票数
        return dic[True] - dic[False]

    def get_upvoters(self):
        """赞同的用户"""
        return [vote.user for vote in self.vote.filter(value=True)]

    def get_downvoters(self):
        """反对的用户"""
        return [vote.user for vote in self.vote.filter(value=False)]

    def accpet_answer(self):
        """接受回答，只能采纳一个回答"""
        answer_set = Answer.objects.filter(question=self.question)  # 得到该回答的问题的所有回答
        answer_set.update(is_answer=False)  # 首先将全部回答置未接受
        # 接受当前回答
        self.is_answer = True
        self.save()
        self.question.has_answer = True
        self.question.save()
