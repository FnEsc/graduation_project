from django.test import RequestFactory  # 这是测view的一种方法
from django.test.client import Client  # 这是view测试的第二种方法
from django.urls import reverse # 这里是由name解析

from test_plus.test import TestCase
from zanhu.news.models import News


class TestNewsViews(TestCase):

    def setUp(self):
        self.user01 = self.make_user("user01", password="password")
        self.user02 = self.make_user("user02", password="password")

        self.client01 = Client()
        self.client02 = Client()

        self.client01.login(username="user01", password="password")
        self.client02.login(username="user02", password="password")

        self.first_news = News.objects.create(
            user=self.user01,
            content="user01的第一条动态"
        )

        self.second_news = News.objects.create(
            user=self.user01,
            content="user01的第二条动态"
        )

        self.third_news = News.objects.create(
            user=self.user02,
            content="user02对user01第一条动态的评论",
            reply=True,
            parent=self.first_news
        )

    def test_news_list(self):
        """测试动态列表页功能"""
        response = self.client01.get(reverse("news:list"))  # 这里的news:list是指news应用下url_name为list
        assert response.status_code == 200
        assert self.first_news in response.context["news_list"]  # 这里的news_list是指view返回前端的上下文对象名称context_object_name
        assert self.second_news in response.context["news_list"]
        assert self.third_news not in response.context["news_list"]

    def test_news_delete(self):
        """删除动态"""
        initial_count = News.objects.count()
        response = self.client01.post(reverse("news:delete_news",kwargs={"pk": self.second_news.pk})) # 发送post请求到url_name，传递primer key
        assert response.status_code == 302
        assert News.objects.count() == initial_count -1

    def test_post_news(self):
        """发送动态"""
        initial_count = News.objects.count()
        response = self.client01.post(
            reverse("news:post_news"),
            {"post": "user01发送post_news请求测试"},
            HTTP_X_REQUESTED_WITH = "XMLHttpRequest" # 表示发送Ajax Request请求
        )
        assert response.status_code == 200
        assert News.objects.count() == initial_count + 1

    def test_like(self):
        """测试点赞"""
        response = self.client01.post(
            path = reverse("news:post_like"),
            data = {"news": self.first_news.pk}, # user01给first_news点赞，
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"  # 表示发送Ajax Request请求
        )
        assert response.status_code == 200
        assert self.first_news.count_likers() == 1
        assert self.user01 in self.first_news.get_likers()
        assert response.json()["likes"] == 1

        response = self.client01.post(
            path=reverse("news:post_like"),
            data={"news": self.first_news.pk},  # user01给first_news取消点赞，
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"  # 表示发送Ajax Request请求
        )
        assert response.status_code == 200
        assert self.first_news.count_likers() == 0
        assert self.user01 not in self.first_news.get_likers()
        assert response.json()["likes"] == 0 # 测试返回的json数据

    def test_get_thread(self):
        """获取动态的评论"""
        response = self.client01.get(
            path=reverse("news:get_thread"),
            data={"news": self.first_news.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"  # 表示发送Ajax Request请求
        )
        assert response.status_code == 200
        assert response.json()["uuid"] == str(self.first_news.pk) # 这里.pk会返回数据列的格式，需要str处理
        assert "user01的第一条动态" in response.json()["news"] # 测试返回的json数据
        assert "user02对user01第一条动态的评论" in response.json()["thread"]


    def test_post_comment(self):
        """发布评论"""
        initial_count = self.first_news.comment_count()
        response = self.client01.post(
            path=reverse("news:post_comment"),
            data={
                "reply": "user01对user01的第一条动态的评论",
                "parent": self.first_news.pk
            },
            HTTP_X_REQUESTED_WITH = "XMLHttpRequest"  # 表示发送Ajax Request请求
        )
        assert response.status_code == 200
        assert response.json()["comment_count"] == (initial_count + 1)
