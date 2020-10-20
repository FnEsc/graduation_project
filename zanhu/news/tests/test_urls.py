from test_plus.test import TestCase
from zanhu.news.models import News
from django.urls import reverse, resolve  # reverse表示应用到url,resolve表示url到应用


class TestNewsURLs(TestCase):
    def setUp(self):
        self.user = self.make_user()
        self.first_news = News.objects.create(
            user=self.user,
            content="user01的第一条动态"
        )

    def test_list(self):
        assert reverse("news:list") == "/news/"
        assert resolve("/news/").view_name == "news:list"

    def test_post_news(self):
        assert reverse("news:post_news") == "/news/post-news/"
        assert resolve("/news/post-news/").view_name == "news:post_news"

    def test_delete_news(self):
        assert (
            reverse("news:delete_news", kwargs={"pk": self.first_news.pk})
            == f"/news/delete/{self.first_news.pk}/"
        )
        assert resolve(f"/news/delete/{self.first_news.pk}/").view_name == "news:delete_news"  # f表示格式化带入python语言

    def test_post_like(self):
        assert reverse("news:post_like") == "/news/like/"
        assert resolve("/news/like/").view_name == "news:post_like"

    def test_get_thread(self):
        assert reverse("news:get_thread") == "/news/get-thread/"
        assert resolve("/news/get-thread/").view_name == "news:get_thread"

    def test_post_comment(self):
        assert reverse("news:post_comment") == "/news/post-comment/"
        assert resolve("/news/post-comment/").view_name == "news:post_comment"
