from test_plus.test import TestCase


class TestUser(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test__str__(self):
        self.assertEquals(self.user.__str__(), 'testuser')

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(),'/users/testuser/')

    def test_get_profile_name(self):
        assert self.user.get_profile_name() == 'testuser'
        self.user.nickname = 'testuser_nickname'
        assert self.user.get_profile_name() == 'testuser_nickname'
