from django.urls import reverse_lazy  # reverse表示应用到url,resolve表示url到应用
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required  # 这个是装饰器，可用于无类的函数view
from django.contrib.auth.mixins import LoginRequiredMixin  # 这个是继承类
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, ListView, DeleteView, DetailView

from zanhu.helpers import ajax_required
from zanhu.question.models import Question, Answer
from zanhu.question.forms import QuestionForm

from zanhu.notifications.views import notification_handler


class QuestionListView(LoginRequiredMixin, ListView):
    """所有问题页"""
    model = Question
    paginate_by = 20
    context_object_name = "questions"  # 配合前端
    template_name = "question/question_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QuestionListView, self).get_context_data()  # 这里拿到重载父类方法的context
        context["popular_tags"] = Question.objects.get_counted_tags()  # 页面的标签
        context["active"] = "all"  # 前端的tab页
        return context


class AnsweredQuestionListView(QuestionListView):
    """已有最佳回答的问题"""

    def get_queryset(self):
        """进行过滤"""
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data()
        context["active"] = "answered"
        return context


class UnansweredQuestionListView(QuestionListView):
    """未有最佳回答的问题"""

    def get_queryset(self):
        """进行过滤"""
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UnansweredQuestionListView, self).get_context_data()
        context["active"] = "unanswered"
        return context


class QuestionCreateView(LoginRequiredMixin, CreateView):
    """用户创建问题"""
    form_class = QuestionForm
    template_name = "question/question_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(QuestionCreateView, self).form_valid(form)

    def get_success_url(self):
        """创建成功后跳转"""
        message = "问题已创建！"
        messages.success(self.request, message)
        return reverse_lazy("question:list")


class QuetsionDetailView(LoginRequiredMixin, DetailView):
    """问题详情页"""
    model = Question
    context_object_name = "question"
    template_name = "question/question_detail.html"


class AnswerCreateView(LoginRequiredMixin, CreateView):
    """回答问题"""
    model = Answer
    fields = ["content", ]  # 用户需要填写的表单只有内容这个字段
    template_name = "question/answer_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs[
            "question_id"]  # 前端form post到propose_answer/<int:question_id> question问题的pk是id
        return super(AnswerCreateView, self).form_valid(form)

    def get_success_url(self):
        """创建成功后跳转"""
        message = "回答问题成功！"
        messages.success(self.request, message)
        return reverse_lazy("question:question_detail", kwargs={"pk": self.kwargs["question_id"]})


@login_required
@ajax_required
@require_http_methods(["POST"])
def question_vote(request):
    """给问题投票，ajax_post请求"""
    question_id = request.POST["question"]  # js前端参数
    value = True if request.POST["value"] == "U" else False  # value表示前端点的是哪个按钮得到的值
    question = Question.objects.get(pk=question_id)

    users = question.vote.values_list("user", flat=True)
    # 获取当前问题的所有投票用户，flat=True表示返回一元组。
    # 注意：values_list这里返回的是值。返回的是用户__str__（我们定义为username）而不是用户对象

    # # 逻辑方法一：
    # # 1.用户首次操作，点赞/踩
    # # 2.用户已赞过，要取消赞/补踩
    # # 3.用户已踩过，要取消踩/补赞
    # # 注意逻辑：重复赞/踩表示取消赞/踩
    # # 1.用户首次操作，点赞/踩
    # if request.user.pk not in users:
    #     question.vote.create(user=request.user, value=value)
    # # 2.用户已赞过，要取消赞/补踩
    # elif question.vote.get(user=request.user).value:
    #     if value: # 赞过继续要赞（即取消赞）
    #         question.vote.get(user=request.user).delete()
    #     else: # 赞过要踩
    #         question.vote.update(user=request.user, value=value)
    # # 3.用户已踩过，要取消踩/补赞
    # else:
    #     if value: # 踩过要赞
    #         question.vote.update(user=request.user, value=value)
    #     else: # 踩过要踩（即取消踩）
    #         question.vote.get(user=request.user).delete()

    # 逻辑方法二：
    # 使用update_or_create()
    # 用户已赞/已踩 且 点击相同按钮
    if request.user.pk in users and (question.vote.get(user=request.user).value == value):
        question.vote.get(user=request.user).delete()
        voted = False
    # 第一次点击 或 点击相反
    else:
        question.vote.update_or_create(user=request.user, defaults={"value": value})
        voted = True

    return JsonResponse({"votes": question.total_votes(), "voted": voted})


@login_required
@ajax_required
@require_http_methods(["POST"])
def answer_vote(request):
    """给回答投票，ajax_post请求"""
    answer_id = request.POST["answer"]  # js前端参数
    value = True if request.POST["value"] == "U" else False  # value表示前端点的是哪个按钮得到的值
    # answer = Answer.objects.get(uuid_id=answer_id) # 这里需要填写uuid_id，因为uuid_id不是唯一
    answer = Answer.objects.get(pk=answer_id)

    users = answer.vote.values_list("user", flat=True)
    # 获取当前问题的所有投票用户，flat=True表示返回一元组。
    # 注意：values_list这里返回的是值。返回的是用户__str__（我们定义为username）而不是用户对象

    # 逻辑方法二：
    # 使用update_or_create()
    # 用户已赞/已踩 且 点击相同按钮
    if request.user.pk in users and (answer.vote.get(user=request.user).value == value):
        answer.vote.get(user=request.user).delete()
        voted = False
    # 第一次点击 或 点击相反
    else:
        # update_or_create 中 defaults 字典来来决定是新增还是更新
        answer.vote.update_or_create(user=request.user, defaults={"value": value})  # 这里传参必须是defaults而不是赋值，这样可以
        voted = True

    return JsonResponse({"votes": answer.total_votes(), "voted": voted})


@login_required
@ajax_required
@require_http_methods(["POST"])
def accept_answer(request):
    """
    接受 ajax post 请求
    已经被接受的回答，用户不能取消，只能更换其他更好的唯一回答
    """
    answer_id = request.POST["answer"]
    answer = Answer.objects.get(pk=answer_id)

    # 验证当前登录用户为问题发起人
    if answer.question.user.username != request.user.username:
        # 注意这里需要用值且类型均相同作为判断，不建议用对象做是否相等的判断
        raise PermissionDenied

    answer.accpet_answer()

    # 通知回答者
    notification_handler(request.user, answer.user, "W", answer)

    return JsonResponse({"status":"true"})

