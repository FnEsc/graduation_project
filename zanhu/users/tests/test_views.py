from test_plus.test import TestCase
from django.test import RequestFactory
from django.contrib import messages

from zanhu.users.models import User
from zanhu.users.views import UserRedirectView, UserUpdateView


class BaseUserTestCase(TestCase):
    def setUp(self):
        self.user = self.make_user()


class TestUserUpdateView(BaseUserTestCase):

    def setUp(self):
        super().setUp()
        self.view = UserUpdateView()
        request = RequestFactory().get("/fake-url/")
        request.user = self.user
        self.view.request = request

    def test_get_success_url(self):
        assert self.view.get_success_url() == f"/users/{self.user.username}/"

    def test_get_object(self):
        assert self.view.get_object() == self.user


class TestUserRedirectView(BaseUserTestCase):
    def test_get_redirect_url(self):
        view = UserRedirectView()
        request = RequestFactory().get("/fake-url")
        request.user = self.user

        view.request = request

        assert view.get_redirect_url() == f"/users/{self.user.username}/"
