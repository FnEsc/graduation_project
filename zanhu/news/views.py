from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse,reverse_lazy

from zanhu.news.models import News
from zanhu.helpers import ajax_required, AuthorRequiredMixin


class NewListView(LoginRequiredMixin, ListView):
    """home_news"""
    model = News
    paginate_by = 20  # 20个分页
    page_kwarg = "page"  # url中的?page=
    context_object_name = "news_list"  # 默认是`模型类名_list`或者`object_list`，回传到前端显示的变量
    ordering = "created_at"  # ("x","y")多个排序元素就这样写
    template_name = "news/news_list.html"

    # def get_ordering(self):
    #     """更多的排序方法"""
    #     pass

    # def get_paginate_by(self, queryset):
    #     """更多的分页方法"""
    #     pass

    def get_queryset(self):
        return News.objects.filter(reply=False)  # 过滤器

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     """更多的上下文对象需要回传到前端"""
    #     context = super().get_context_data()
    #     context["view_count"] = 100
    #     return context

@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    """发送动态，ajax post请求"""
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string("news/news_single.html",{"news":posted, "request": request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空！")


class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = News
    template_name = "news/news_confirm_delete.html"
    slug_url_kwarg = "slug" # 通过url传入要删除的对象主键id，默认值是slug
    pk_url_kwarg = "pk" # 通过url传入要删除的对象主键id，默认值是pk
    success_url = reverse_lazy("news:list") # reverse_lazy允许在项目URLConf未加载前使用


@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    """点赞，ajax post请求"""
    news_id = request.POST["news"] # 前端js代码传入参数为news:uuid
    news = News.objects.get(pk=news_id) # 获取到news对象
    news.switch_like(request.user) # 取消或添加赞
    return JsonResponse({"likes": news.count_likers()}) # js前端需要接收json数组

@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    """返回动态的评论，ajax get请求"""
    news_id = request.GET["news"]
    news = News.objects.get(pk=news_id)
    news_html = render_to_string("news/news_single.html",{"news": news})
    thread_html = render_to_string("news/news_thread.html", {"thread": news.get_thread()})
    return JsonResponse({
        "uuid": news_id,
        "news": news_html,
        "thread": thread_html,
    })



@login_required
@ajax_required
@require_http_methods(['POST'])
def post_comment(request):
    """发表评论"""
    post = request.POST["reply"].strip()
    parent_id = request.POST["parent"]
    parent = News.objects.get(pk=parent_id)
    if post:
        # print("stop1: ", request.user, post, parent_id, parent.uuid_id)
        parent.reply_this(request.user, post)
        return JsonResponse({"comment_count": parent.comment_count()})
    else:
        return HttpResponseBadRequest("内容不能为空！")

@login_required
@ajax_required
@require_http_methods(['POST'])
def update_interactions(request):
    """更新互动信息"""
    id_value = request.POST["id_value"]
    news = News.objects.get(pk=id_value)
    return JsonResponse({"likes": news.count_likers(), "comments": news.comment_count()})
