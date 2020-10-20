from test_plus.test import TestCase
from zanhu.news.models import News


class NewsModelsTest(TestCase):
    def setUp(self):
        self.user01 = self.make_user("user01")
        self.user02 = self.make_user("user02")
        self.first_news = News.objects.create(
            user=self.user01,
            content="第一条评论"
        )
        self.second_news = News.objects.create(
            user=self.user02,
            content="第二条评论"
        )
        self.third_news = News.objects.create(
            user=self.user01,
            content="user01评论第一条动态",
            reply=True,
            parent=self.first_news
        )

    def test__str__(self):
        self.assertEquals(self.first_news.__str__(), "第一条评论")

    def test_switch_like(self):
        """测试赞或取消赞功能"""
        self.first_news.switch_like(self.user01)  # user01给first_news点赞
        assert self.first_news.count_likers() == 1
        assert self.user01 in self.first_news.get_likers()

        self.first_news.switch_like(self.user01)  # user01给first_news取消点赞
        assert self.first_news.count_likers() == 0
        assert self.user01 not in self.first_news.get_likers()

    def test_reply_this(self):
        """测试回复功能"""
        initial_count = News.objects.count()
        self.first_news.reply_this(self.user02, "user02评论第一条动态")
        assert News.objects.count() == initial_count + 1
        assert self.first_news.comment_count() == 2  # 一共有两条评论
        assert self.third_news in self.first_news.get_thread()
