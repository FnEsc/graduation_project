from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django_comments.signals import comment_was_posted

from zanhu.article.models import Article
from zanhu.article.forms import ArticleForm
from zanhu.notifications.views import notification_handler
from zanhu.helpers import AuthorRequiredMixin


class ArticleListView(LoginRequiredMixin, ListView):
    """已发表的文章列表"""
    model = Article
    paginate_by = 10
    context_object_name = "articles"  # 默认上下文对象名称为models名称，这里返回多个文章，所以用articles
    template_name = "article/article_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        """增加tag标签返回"""
        context = super().get_context_data()
        context["popular_tags"] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_published()


class DraftListView(ArticleListView):
    """草稿箱列表"""

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).get_drafts()


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """发表文章视图"""
    model = Article
    form_class = ArticleForm  # 使用模型类的form
    template_name = "article/article_create.html"

    def form_valid(self, form):
        """将user填充进去Article表单里"""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """创建成功后跳转"""
        message = "文章已创建！"
        messages.success(self.request, message)
        return reverse_lazy("article:list")


class ArticleDetailView(LoginRequiredMixin, DeleteView):
    """文章详情页"""
    model = Article
    context_object_name = "article" # 与前端保持一致
    template_name = "article/article_detail.html"

    # pk、slug均为默认的，不需要手动定义


class ArticleEditView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView): # 注意类的继承顺序
    """编辑文章"""
    model = Article
    form_class = ArticleForm
    template_name = "article/article_update.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """编辑成功后跳转"""
        message = "文章编辑成功！"
        messages.success(self.request, message)
        return reverse_lazy("article:article", kwargs={"slug":self.get_object().slug})

def notify_comment(**kwargs):
    """文章有评论时候通知作者"""
    from django_comments.models import Comment
    actor = kwargs["request"].user
    obj = kwargs["comment"].content_object  # 评论的实体对象（实现由外键关联）

    notification_handler(actor, obj.user, "C", obj)

# 观察者模式 = 订阅[列表] + 通知（同步）
comment_was_posted.connect(receiver=notify_comment) # 评论后连接到notify_comment这个目标，由目标函数来处理
