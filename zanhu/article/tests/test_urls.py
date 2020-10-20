from test_plus.test import TestCase
from zanhu.article.models import Article
from zanhu.article import views

from django.urls import reverse, resolve  # reverse表示应用到url,resolve表示url到应用
from django.test import override_settings

from PIL import Image
import tempfile


class ArticleURLsTest(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.first_article = Article.objects.create(
            title = "测试文章标题",
            user=self.user,
            content="测试文章内容",
        )

    def test_list(self):
        assert reverse("article:list") == "/article/"
        assert resolve("/article/").view_name == "article:list"

    def test_write_new(self):
        assert reverse("article:write_new") == "/article/write-new-article/"
        assert resolve("/article/write-new-article/").view_name == "article:write_new"

    def test_drafts(self):
        assert reverse("article:drafts") == "/article/drafts/"
        assert resolve("/article/drafts/").view_name == "article:drafts"

    def test_article(self):

        assert (
            reverse("article:article", kwargs={"slug": self.first_article.slug})
            == f"/article/{self.first_article.slug}/"
        )
        assert resolve(f"/article/{self.first_article.slug}/").view_name == "article:article"  # f表示格式化带入python语言

    def test_edit_article(self):
        assert (
            reverse("article:edit_article", kwargs={"pk": self.first_article.pk})
            == f"/article/edit/{self.first_article.pk}/"
        )
        assert resolve(f"/article/edit/{self.first_article.pk}/").view_name == "article:edit_article"  # f表示格式化带入python语言
