from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "users/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data()
        user = User.objects.get(username=self.request.user.username)
        context["moments_count"] = user.publisher.filter(reply=False).count() # 反向查询
        context["article_count"] = user.author.filter(status="P").count()
        context["comment_count"] = user.publisher.filter(reply=True).count() + user.comment_comments.all().count() # 动态评论数 + django comnent(只用在文章应用)评论数
        context["question_count"] = user.question_author.filter(status="O").count()
        context["answer_count"] = user.answer_author.all().count()

        # 私信用户数
        messages_count = len(set([u.recipient.username for u in user.sent_messages.all()] + [u.sender.username for u in user.received_messages.all()]))

        # 互动数 = 动态点赞数 + 问答数点赞数 + 评论数 + 私信用户数（发送 or 接收私信）
        context["interaction_count"] = user.liked_news.all().count() + user.vote_user.all().count() + context["comment_count"] + \
                                       messages_count

        return context

user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["nickname", "job_title", "introduction", "picture", "city", "personal_url", "weibo", "zhihu", "github",
              "Linkedin"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
