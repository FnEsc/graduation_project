"""
使用TestClient和RequestFactory测试视图的区别

TestClient: 走Django框架的整个请求响应流程，经过WSGI handler、中间件、url路由、上下文处理器，返回response，更像是集成测试。
特点：使用简单，测试一步到位。
缺点：测试用例运行慢，依赖于中间件、url路由等其他部分

RequestFactory：生成WSGIRequest供使用，与Django代码无关，单元测试的最佳实践
缺点：使用难度高
"""

import json
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from test_plus.test import CBVTestCase  # 类视图专用扩展测试类

from zanhu.question.models import Question, Answer
from zanhu.question import views



class BaseQuestionTest(CBVTestCase):

    def setUp(self):
        """初始化操作"""
        self.user01 = self.make_user(username='user01', password='password')
        self.user02 = self.make_user(username='user02', password='password')
        self.question01 = Question.objects.create(
            user=self.user01,
            title="问题01",
            content="问题01的内容",
            tags="测试01,测试02"
        )
        self.question02 = Question.objects.create(
            user=self.user01,
            title="问题02",
            content="问题02的内容",
            has_answer=True,
            tags="测试01,测试02"
        )
        self.answer01 = Answer.objects.create(
            user=self.user01,
            question=self.question02,
            content="问题02的最佳回答",
            is_answer=True
        )

        self.request = RequestFactory().get(
            "/fake-url")  # 因为RequestFactory是用来生成request请求的，这里的测试不会经过路由，所以get请求的url地址并不重要，只是将请求直接传递到由视图views处理
        self.request.user = self.user01


class QuestionListViewTest(BaseQuestionTest):
    """测试问题列表"""

    def test_context_data(self):
        response = self.get(views.QuestionListView, request=self.request)

        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context_data["questions"],
                                 map(repr, [self.question01, self.question02]),
                                 ordered=False)
        self.assertTrue(zip(response.context_data["questions"], Question.objects.all()))
        # (1, 2, 3) (4, 5, 6)   zip(xx, yy)
        # ((1, 4), (2, 5), (3, 6)) 让assertTrue逐个对比1和4、2和5、3和6是否相等

        self.assertTrue(a == b for a, b in zip(response.context_data["questions"], Question.objects.all()))

        self.assertTrue(all(a == b for a, b in zip(response.context_data["questions"], Question.objects.all())))
        # all(True, False, True) = False

        self.assertContext("popular_tags", Question.objects.get_counted_tags())
        self.assertContext("active", "all")


class AnsweredQuestionListViewTest(BaseQuestionTest):
    """测试已回答问题列表"""

    def test_context_data(self):
        # response = self.get(views.AnsweredQuestionListView, request=self.request)
        response = views.AnsweredQuestionListView.as_view()(self.request)

        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(response.context_data["questions"], [repr(self.question02)])

        # self.assertContext("actice", "answered") # 注意：如果使用as_view则不能使用self.assertContext
        # 如果是使用self.get()得到response，则可以使用self.assertContext
        self.assertEqual(response.context_data["active"], "answered")


class UnansweredQuestionListViewTest(BaseQuestionTest):
    """测试未回答问题列表"""

    def test_context_data(self):
        response = self.get(views.UnansweredQuestionListView, request=self.request)
        # self.assertEqual(response.status_code, 200)
        self.response_200(response)  # 判断response状态码是否为200
        self.assertQuerysetEqual(response.context_data["questions"], [repr(self.question01)])
        self.assertContext("active", "unanswered")


class QuestionCreateViewTest(BaseQuestionTest):
    """测试创建问题，对继承下来的通用类，我们只需要测试其结果而不是过程或重写的函数"""

    def test_get(self):
        response = self.get(views.QuestionCreateView, request=self.request)
        self.response_200(response)
        self.assertContains(response, "标题")
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")
        self.assertContains(response, "标签")
        self.assertIsInstance(response.context_data["view"], views.QuestionCreateView)  # form会自动加上view对象

    def test_post(self):
        data = {"title": "title_test", "content": "content_test", "tags": "tag1,yag2", "status": "O"}
        request = RequestFactory().post("/fake-url", data=data)
        request.user = self.user01 # self.request已经使用get请求了，因此这里需要再创建RequestFactory()

        # django的message机制在requestfacory测试中需要这样做，来源于django issue
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.QuestionCreateView, request=request)
        assert response.status_code == 302
        assert response.url == "/question/"

class QuetsionDetailViewTest(BaseQuestionTest):
    """测试问题详情页"""
    def test_get_context_data(self):
        response = self.get(views.QuetsionDetailView, request=self.request, pk=self.question01.pk)
        self.response_200(response)
        self.assertEqual(response.context_data["question"], self.question01)

class AnswerCreateViewTest(BaseQuestionTest):
    """测试创建回答"""
    def test_get(self):
        response = self.get(views.AnswerCreateView, request=self.request, question_id=self.question01.id)
        self.response_200(response)
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")
        self.assertIsInstance(response.context_data["view"], views.AnswerCreateView)  # form会自动加上view对象

    def test_post(self):
        request = RequestFactory().post("/fake-url", data={"content": "content_test"})
        request.user = self.user01 # self.request已经使用get请求了，因此这里需要再创建RequestFactory()

        # django的message机制在requestfacory测试中需要这样做，来源与django issue
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.AnswerCreateView, request=request, question_id=self.question01.id)
        assert response.status_code == 302
        assert response.url == "/question/question-detail/%s/" % (self.question01.pk)
        assert response.url == "/question/question-detail/{}/".format(self.question01.pk)
        assert response.url == f"/question/question-detail/{self.question01.pk}/" # f特性是python3.6的新特性

class VoteTest(BaseQuestionTest):
    """测试投票功能"""

    def setUp(self):
        super(VoteTest, self).setUp()
        self.request = RequestFactory().post("/fake-url", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        # This QueryDict instance is immutable  request.POST是QueryDict对象，不可变的
        self.request.POST = self.request.POST.copy()
        self.request.user = self.user02

    def test_question_vote_up(self):
        self.request.POST["question"] = self.question01.id # 改变POST是request.POST即QueryDict对象的属性
        self.request.POST["value"] = "U"

        response = views.question_vote(self.request) # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == 1
        assert json.loads(response.content)["voted"] == True

        response = views.question_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == 0
        assert json.loads(response.content)["voted"] == False

    def test_question_vote_down(self):
        self.request.POST["question"] = self.question01.id  # 改变POST是request.POST即QueryDict对象的属性
        self.request.POST["value"] = "D"

        response = views.question_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == -1
        assert json.loads(response.content)["voted"] == True

        response = views.question_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == 0
        assert json.loads(response.content)["voted"] == False

    def test_answer_vote_up(self):
        self.request.POST["answer"] = self.answer01.pk  # 改变POST是request.POST即QueryDict对象的属性
        self.request.POST["value"] = "U"

        response = views.answer_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == 1
        assert json.loads(response.content)["voted"] == True

        response = views.answer_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == 0
        assert json.loads(response.content)["voted"] == False

    def test_answer_vote_down(self):
        self.request.POST["answer"] = self.answer01.pk  # 改变POST是request.POST即QueryDict对象的属性
        self.request.POST["value"] = "D"

        response = views.answer_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == -1
        assert json.loads(response.content)["voted"] == True

        response = views.answer_vote(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()
        assert response.status_code == 200
        assert json.loads(response.content)["votes"] == 0
        assert json.loads(response.content)["voted"] == False

class Accept_answerTest(BaseQuestionTest):
    """测试采纳回答"""
    def setUp(self):
        super(Accept_answerTest, self).setUp()
        self.answer02 = Answer.objects.create(
            user=self.user02,
            question=self.question01,
            content="user02给user01的问题01回答：answer02",
        )
        self.answer03 = Answer.objects.create(
            user=self.user02,
            question=self.question01,
            content="user02给user01的问题01回答：answer03",
        )

        self.request = RequestFactory().post("/fake-url", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        # This QueryDict instance is immutable  request.POST是QueryDict对象，不可变的
        self.request.POST = self.request.POST.copy()
        self.request.user = self.user01

    def test_accept_answer(self):
        # 采纳最佳答案
        self.request.POST["answer"] = self.answer02.pk
        response = views.accept_answer(self.request)  # 测试是一个函数，如果是类则RequestFactory().post()

        self.response_200(response)
        assert json.loads(response.content)["status"] == "true"

