from test_plus.test import TestCase
from zanhu.article.models import Article
from django.test.client import Client
from django.urls import reverse # 这里是由name解析

import tempfile
from PIL import Image

from django.test import override_settings

class ArticleViewTest(TestCase):

    @staticmethod
    def get_tmp_image():
        """创建并读取临时图片文件"""
        size = (200, 200)
        color = (255, 0, 0, 0)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image = Image.new("RGB", size, color)
            image.save(f,"PNG")
        return open(f.name, mode="rb")

    def setUp(self):
        """初始化操作"""
        self.user = self.make_user(username='testuser', password='password')
        self.first_article = Article.objects.create(
            title = "测试文章标题01",
            user=self.user,
            content="测试文章内容01",
        )
        self.second_article = Article.objects.create(
            title="测试文章标题02",
            user=self.user,
            status="P",
            content="测试文章内容02",
        )
        self.test_image = self.get_tmp_image()

        self.client = Client()
        self.client.login(username='testuser', password='password')


    def tearDown(self): # 该函数是每个用例结束后都会执行一次
        """测试结束时关闭临时图片"""
        self.test_image.close()

    def test_index_article(self):
        """测试文章发布、草稿列表页、文章详情页"""
        # 发布页
        response = self.client.get(reverse("article:list"))
        assert response.status_code == 200          # 测试方法1
        self.assertEqual(response.status_code, 200) # 测试方法2
        assert self.first_article not in response.context["articles"]
        assert self.second_article in response.context["articles"]
        # 草稿页
        response = self.client.get(reverse("article:drafts"))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.first_article in response.context["articles"]
        assert self.second_article not in response.context["articles"]
        # 详情页
        response = self.client.get(reverse("article:article",kwargs={"slug":self.first_article.slug}))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.first_article == response.context["article"]

    def test_error_404(self):
        """访问一篇不存在的文章"""
        # 访问文章页
        response = self.client.get(reverse("article:article",kwargs={"slug":"no-slug"}))
        assert response.status_code == 404          # 测试方法1
        self.assertEqual(response.status_code, 404) # 测试方法2
        # 编辑文章页
        response = self.client.get(reversed("aericle/edit/-1")) # 测试编辑pk=-1的文章
        assert response.status_code == 404  # 测试方法1
        self.assertEqual(response.status_code, 404)  # 测试方法2

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_article(self):
        """文章创建成功并跳转"""
        initial_count = Article.objects.count()
        response = self.client.post(
            reverse("article:write_new"),
            data={
                "title": "测试test_create_article标题",
                "content": "测试test_create_article内容",
                "tags": "测试test_create_article标签01,测试test_create_article标签02",
                "status": "P",
                "image": self.test_image
            }
        ) # 提交post请求创建发表文章
        assert response.status_code == 302 # 301永久重定向，url改变，302临时重定向，Url不变
        assert Article.objects.count() == initial_count + 1

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_draft(self):
        """测试发布草稿箱功能"""
        initial_count = Article.objects.count()
        response = self.client.post(
            reverse("article:write_new"),
            data={
                "title": "测试草稿标题",
                "content": "测试草稿内容",
                "tags": "测试草稿标签01,测试草稿标签02",
                "status": "D",
                "image": self.test_image
            }
        )  # 提交post请求创建草稿文章
        assert response.status_code == 302
        response = self.client.get(reverse("article:drafts"))
        assert response.status_code == 200
        index = len(response.context["articles"]) - 1
        assert response.context["articles"][index].slug == "ce-shi-cao-gao-biao-ti" # 得到最后一个草稿的slug


    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_draft_edit_to_article(self):
        """测试由草稿箱发表文章"""
        response = self.client.post(
            reverse("article:write_new"),
            data={
                "title": "测试最后草稿标题",
                "content": "测试最后草稿内容",
                "tags": "测试草稿标签01,测试草稿标签02",
                "status": "D",
                "image": self.test_image
            }
        )  # 提交post请求创建最后的草稿文章
        response = self.client.get(reverse("article:drafts"))
        assert response.status_code == 200
        index = len(response.context["articles"]) - 1
        pk = response.context["articles"][index].pk
        response = self.client.get(reverse("article:edit_article",kwargs={"pk":pk}))
        assert response.context["article"].title == "测试最后草稿标题"





