from django.test import TestCase
from custom_auth.models import UserAccount, validate_phone_number


class TestModels(TestCase):
    def setUp(self):
        self.credentials = {
            "email": "test_user1@example.com",
            "username": "test_user1",
            "password": "test_password1",
        }

    def test_create_user(self):
        test_user = UserAccount.objects.create_user(**self.credentials)
        self.assertEqual(UserAccount.objects.get(username="test_user1"), test_user)

    def test_create_superuser(self):
        test_superuser = UserAccount.objects.create_superuser(**self.credentials)
        self.assertEqual(UserAccount.objects.get(username="test_user1"), test_superuser)
        self.assertEqual(test_superuser.is_superuser, True)

    def test_validate_phone_number(self):
        self.assertEqual(validate_phone_number("9923922234"), "9923922234")
