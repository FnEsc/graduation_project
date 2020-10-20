from test_plus.test import TestCase
from zanhu.question.models import Question, Answer
from zanhu.question import views

from django.urls import reverse, resolve


class QuestionURLsTest(TestCase):

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

    def test_list(self):
        assert reverse("question:list") == "/question/"
        assert resolve("/question/").view_name == "question:list"

    def test_all_q(self):
        assert reverse("question:all_q") == "/question/all/"
        assert resolve("/question/all/").view_name == "question:all_q"

    def test_unanswered_q(self):
        assert reverse("question:unanswered_q") == "/question/unanswered/"
        assert resolve("/question/unanswered/").view_name == "question:unanswered_q"

    def test_answered_q(self):
        assert reverse("question:answered_q") == "/question/answered/"
        assert resolve("/question/answered/").view_name == "question:answered_q"

    def test_ask_question(self):
        assert reverse("question:ask_question") == "/question/ask-question/"
        assert resolve("/question/ask-question/").view_name == "question:ask_question"

    def test_question_detail(self):
        assert reverse("question:question_detail",kwargs={"pk":self.question01.pk}) == f"/question/question-detail/{self.question01.pk}/"
        assert resolve(f"/question/question-detail/{self.question01.pk}/").view_name == "question:question_detail"

    def test_propose_answer(self):
        assert reverse("question:propose_answer",kwargs={"question_id":self.question01.pk}) == f"/question/propose-answer/{self.question01.pk}/"
        assert resolve(f"/question/propose-answer/{self.question02.pk}/").view_name == "question:propose_answer"

    def test_question_vote(self):
        assert reverse("question:question_vote") == "/question/question-vote/"
        assert resolve("/question/question-vote/").view_name == "question:question_vote"

    def test_answer_vote(self):
        assert reverse("question:answer_vote") == "/question/answer-vote/"
        assert resolve("/question/answer-vote/").view_name == "question:answer_vote"

    def test_accept_answer(self):
        assert reverse("question:accept_answer") == "/question/accept-answer/"
        assert resolve("/question/accept-answer/").view_name == "question:accept_answer"
