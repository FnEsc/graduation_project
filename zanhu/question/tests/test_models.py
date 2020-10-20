from test_plus.test import TestCase

from zanhu.question.models import Question, Answer


class QuestionModelTest(TestCase):  # Question应用下的models测试
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

    def test_vote_question(self):
        """给问题投票"""
        self.question01.vote.update_or_create(user=self.user01, defaults={"value": True})
        self.question01.vote.update_or_create(user=self.user02, defaults={"value": True})
        assert self.question01.total_votes() == 2

    def test_vote_answer(self):
        """给回答投票"""
        self.answer01.vote.update_or_create(user=self.user01, defaults={"value": True})
        self.answer01.vote.update_or_create(user=self.user02, defaults={"value": True})
        assert self.answer01.total_votes() == 2

    def test_get_question_voters(self):
        """问题的投票用户"""
        self.question01.vote.update_or_create(user=self.user01, defaults={"value": True})
        self.question01.vote.update_or_create(user=self.user02, defaults={"value": False})
        assert self.user01 in self.question01.get_upvoters()
        assert self.user02 not in self.question01.get_upvoters()
        assert self.user01 not in self.question01.get_downvoters()
        assert self.user02 in self.question01.get_downvoters()

    def test_get_answer_voters(self):
        """回答的投票用户"""
        self.answer01.vote.update_or_create(user=self.user01, defaults={"value": True})
        self.answer01.vote.update_or_create(user=self.user02, defaults={"value": False})
        assert self.user01 in self.answer01.get_upvoters()
        assert self.user02 not in self.answer01.get_upvoters()
        assert self.user01 not in self.answer01.get_downvoters()
        assert self.user02 in self.answer01.get_downvoters()

    def test_unanswer_question(self):
        """未有回答的问题"""
        assert self.question01 in Question.objects.get_unanswered()
        assert self.question02 not in Question.objects.get_unanswered()

    def test_answered_question(self):
        """已有最佳回答的问题"""
        assert self.question02 in Question.objects.get_answered()
        assert self.question01 not in Question.objects.get_answered()

    def test_question_get_answers(self):
        """获取问题的所有回答"""
        assert self.answer01 == self.question02.get_answers()[0]
        assert self.question02.count_answers() == 1
        assert self.question01.count_answers() == 0

    def test_question_accept_answer(self):
        """提问者接受回答"""
        answer02 = Answer.objects.create(
            user=self.user01,
            question=self.question01,
            content="回答02"
        )
        answer03 = Answer.objects.create(
            user=self.user01,
            question=self.question01,
            content="回答03"
        )
        answer04 = Answer.objects.create(
            user=self.user01,
            question=self.question01,
            content="回答04"
        )
        self.assertFalse(answer02.is_answer)
        self.assertFalse(answer03.is_answer)
        self.assertFalse(answer04.is_answer)
        self.assertFalse(self.question01.has_answer)
        # 接受回答answer02
        answer02.accpet_answer()
        self.assertTrue(answer02)
        self.assertTrue(self.question01.has_answer)
        self.assertFalse(answer03.is_answer)
        self.assertFalse(answer04.is_answer)

    def test_question_str(self):
        assert isinstance(self.question01, Question)
        assert self.question01.__str__() == "问题01"

    def test_answer_str(self):
        assert isinstance(self.answer01, Answer)
        assert self.answer01.__str__() == "问题02的最佳回答"
