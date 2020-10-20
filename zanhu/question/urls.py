from django.urls import path
from zanhu.question import views

app_name = "question" # 当前配置所在appname
urlpatterns = [
    path("", view=views.QuestionListView.as_view(), name="list"),
    path("unanswered/", view=views.UnansweredQuestionListView.as_view(), name="unanswered_q"),
    path("answered/", view=views.AnsweredQuestionListView.as_view(), name="answered_q"),
    path("all/", view=views.QuestionListView.as_view(), name="all_q"),
    path("ask-question/", view=views.QuestionCreateView.as_view(), name="ask_question"),
    path("question-detail/<int:pk>/", view=views.QuetsionDetailView.as_view(), name="question_detail"),
    path("propose-answer/<int:question_id>/", view=views.AnswerCreateView.as_view(), name="propose_answer"), # 前端的是通过question.id 或者 view.kwargs.question_id传递到后台的
    path("question-vote/", view=views.question_vote, name="question_vote"),
    path("answer-vote/", view=views.answer_vote, name="answer_vote"),
    path("accept-answer/", view=views.accept_answer, name="accept_answer"),
]
