from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from slugify import slugify  # 用于生成url别名
from taggit.managers import TaggableManager

from django_comments.models import Comment

@python_2_unicode_compatible
class ArticleQuerySet(models.query.QuerySet):
    """自定义QuerySet，提高模型类的可用性"""
    def get_published(self):
        """获取已发表的文章"""
        return self.filter(status="P")

    def get_drafts(self):
        """获取草稿文章"""
        return self.filter(status="D")

    def get_counted_tags(self):
        """统计所有已发表的文章中，每一个标签的数量（大于0的）"""
        tag_dict = {}
        query = self.get_published() # 如果贴上标签，则都会大于0而返回，所以不需要过滤大于0 .annotate(tagged=models.Count("tags")).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()

# Create your models here.
@python_2_unicode_compatible
class Article(models.Model):
    STATUS = (("D", "Draft"), ("P", "Published"))

    title = models.CharField(max_length=255, unique=True, verbose_name="文章标题")  # verbose_name不是sql的注释，这里是作为python查询的别名
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="author", on_delete=models.SET_NULL)
    image = models.ImageField(upload_to="article_pic/%Y/%m/%d", verbose_name="文章图片")
    slug = models.SlugField(max_length=255, verbose_name="(URL)别名")  # 主流浏览器url至少支持2083个字符
    status = models.CharField(max_length=1, choices=STATUS, default="D", verbose_name="文章状态")
    content = MarkdownxField(verbose_name="文章内容")
    editable = models.BooleanField(default=False, verbose_name="是否可编辑")
    tags = TaggableManager(help_text="多个标签使用,(英文)隔开", verbose_name="标签")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = ArticleQuerySet.as_manager() # 关联该类的自定义查询集

    class Meta:
        verbose_name_plural = verbose_name = "文章"
        ordering = ("created_at",)

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)
        super(Article, self).save()  # python2的写法是：super().save()

    def get_markdown(self):
        """将markdown文本渲染成html"""
        return markdownify(self.content)
