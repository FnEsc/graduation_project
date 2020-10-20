from test_plus.test import TestCase
from zanhu.article.models import Article


class ArticleModelsTest(TestCase):

    def setUp(self):
        """初始化操作"""
        self.user = self.make_user()
        self.first_article = Article.objects.create(
            title="测试文章标题01",
            user=self.user,
            status="D",
            content="测试文章内容01",
        )
        self.second_article = Article.objects.create(
            title="测试文章标题02",
            user=self.user,
            status="P",
            content="测试文章内容02",
        )

    def test_object_instance(self):
        """判断实例对象是否为Article模型类"""
        assert isinstance(self.first_article, Article)
        assert isinstance(self.second_article, Article)
        assert isinstance(Article.objects.get_published()[0],Article)
        assert isinstance(Article.objects.get_drafts()[0], Article)

    def test_return_values(self):
        """测试返回值"""
        assert self.first_article.status == "D"
        assert self.first_article.status != "P"
        assert self.second_article.__str__() == "测试文章标题02"
        assert self.first_article in Article.objects.get_drafts()
        assert self.second_article in Article.objects.get_published()
        assert Article.objects.get_drafts()[0].title =="测试文章标题01"
        assert Article.objects.get_published()[0].title =="测试文章标题02"

