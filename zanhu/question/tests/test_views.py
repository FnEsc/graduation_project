from test_plus.test import TestCase
from zanhu.question.models import Question, Answer
from django.test.client import Client
from django.urls import reverse  # 这里是由name解析
import json

class QuestionViewTest(TestCase):

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

        self.client01 = Client()
        self.client01.login(username='user01', password='password')
        self.client02 = Client()
        self.client02.login(username='user02', password='password')

    def test_question_list(self):
        """测试问题页：所有问题、已采纳答案的问题、未采纳的问题"""
        response = self.client01.get(reverse("question:list"))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.question01 in response.context["questions"]
        assert self.question02 in response.context["questions"]

        response = self.client01.get(reverse("question:all_q"))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.question01 in response.context["questions"]
        assert self.question02 in response.context["questions"]

        response = self.client01.get(reverse("question:answered_q"))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.question01 not in response.context["questions"]
        assert self.question02 in response.context["questions"]

        response = self.client01.get(reverse("question:unanswered_q"))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.question01 in response.context["questions"]
        assert self.question02 not in response.context["questions"]

    def test_question_detail(self):
        """访问一个问题"""
        response = self.client01.get(reverse("question:question_detail", kwargs={"pk": self.question01.pk}))
        assert response.status_code == 200  # 测试方法1
        self.assertEqual(response.status_code, 200)  # 测试方法2
        assert self.question01 == response.context["question"]

        response = self.client01.get(reverse("question:question_detail", kwargs={"pk": 0}))
        assert response.status_code == 404  # 测试方法1
        self.assertEqual(response.status_code, 404)  # 测试方法2

    def test_create_question(self):
        """创建问题"""
        initial_count = Question.objects.count()
        response = self.client01.post(
            reverse("question:ask_question"),
            data={
                "title": "测试test_create_question标题",
                "content": "测试test_create_question内容",
                "tags": "tag1,tag2",
                "status": "O"
            }
        )
        assert response.status_code == 302
        assert Question.objects.count() == initial_count + 1

    def test_create_answer(self):
        """创建回答"""
        initial_count = Answer.objects.count()
        response = self.client01.post(
            reverse("question:propose_answer", kwargs={"question_id": self.question01.pk}),
            data={
                "content": "test_create_answer"
            }
        )
        assert response.status_code == 302
        assert Answer.objects.count() == initial_count + 1

    def test_question_vote(self):
        """测试问题投票"""
        # 投票赞成
        response = self.client01.post(
            path=reverse("question:question_vote"),
            data={
                "question": self.question01.pk,
                "value": "U",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert self.question01.total_votes() == 1

        response = self.client02.post(
            path=reverse("question:question_vote"),
            data={
                "question": self.question01.pk,
                "value": "D",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert self.question01.total_votes() == 0

    def test_answer_vote(self):
        """测试回答投票"""
        # 投票赞成
        response = self.client01.post(
            path=reverse("question:answer_vote"),
            data={
                "answer": self.answer01.pk,
                "value": "U",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert self.answer01.total_votes() == 1

        response = self.client02.post(
            path=reverse("question:answer_vote"),
            data={
                "answer": self.answer01.pk,
                "value": "D",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert self.question01.total_votes() == 0

    def test_accept_answer(self):
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

        # 使用user01采纳answer02答案
        response = self.client01.post(
            path=reverse("question:accept_answer"),
            data={
                "answer": self.answer02.pk
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert json.loads(response.content)["status"] == "true"
