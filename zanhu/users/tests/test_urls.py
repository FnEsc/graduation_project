from test_plus.test import TestCase
from django.urls import reverse,resolve


class TestUserURLs(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_detail(self):
        assert (
            reverse("users:detail", kwargs={"username": self.user.username})
            == f"/users/{self.user.username}/"
        )
        assert resolve(f"/users/{self.user.username}/").view_name == "users:detail" # f表示格式化带入python语言

    def test_update(self):
        assert reverse("users:update") == "/users/~update/"
        assert resolve("/users/~update/").view_name == "users:update"

    def test_redirect(self):
        assert reverse("users:redirect") == "/users/~redirect/"
        assert resolve("/users/~redirect/").view_name == "users:redirect"
