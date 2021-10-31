from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from custom_auth.models import UserAccount
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import json


class TestView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.credentials_user1 = {
            "email": "test_user1@example.com",
            "username": "test_user1",
            "password": "test_password1",
        }
        self.test_user1 = UserAccount.objects.create_user(**self.credentials_user1)
        self.test_user1.first_name = "test_user1_first_name"
        self.test_user1.last_name = "test_user1_last_name"
        self.test_user1.gender = "Female"
        self.test_user1.year = "2nd year"
        self.test_user1.mobile = "9411123411"
        self.test_user1.college_name = "IIT BHU"
        self.test_user1.save()

        self.credentials_user2 = {
            "email": "test_user2@example.com",
            "username": "test_user2",
            "password": "test_password2",
            "first_name": "test_user2_first_name",
            "last_name": "test_user2_last_name",
            "gender": "Female",
            "year": "2nd year",
            "mobile": "9411123411",
            "college_name": "IIT BHU",
            "referral_code": "",
        }

        self.auth_token = Token.objects.get_or_create(user=self.test_user1)
        self.uidb64 = urlsafe_base64_encode(smart_bytes(self.test_user1.id))
        self.token = PasswordResetTokenGenerator().make_token(self.test_user1)

        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.update_url = reverse("update")
        self.register_url = reverse("register")
        self.activate_account_url1 = reverse(
            "activate-account", args=[self.uidb64, self.token]
        )
        self.activate_account_url2 = reverse(
            "activate-account", args=["some-uidb64", "some-token"]
        )
        self.password_reset_email_url = reverse("password-reset-email")
        self.password_reset_confirm_url1 = reverse(
            "password-reset-confirm", args=[self.uidb64, self.token]
        )
        self.password_reset_confirm_url2 = reverse(
            "password-reset-confirm", args=["some-uidb64", "some-token"]
        )

    # Invalid user login
    def test_login_view_401(self):
        response = self.client.post(
            self.login_url,
            {"email_or_username": "test_user1", "password": "test_password1"},
        )
        self.assertEqual(response.status_code, 401)

    # Authenticated user logout
    def test_logout_view_200(self):
        self.client.force_authenticate(user=self.test_user1)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)

    # Unauthenticated user logout
    def test_logout_view_401(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 401)

    # Correct user credentials
    def test_register_view_POST_correct_credentials(self):
        response = self.client.post(self.register_url, self.credentials_user2)
        self.assertEqual(response.status_code, 200)

    # Invalid user credentials
    def test_register_view_POST_invalid_credentials(self):
        self.credentials_user2["mobile"] = "94998aby99"
        response = self.client.post(self.register_url, self.credentials_user2)
        self.assertEqual(response.status_code, 409)

    # User with given credentials already exists
    def test_register_view_POST_same_credentials(self):
        response = self.client.post(
            self.register_url,
            {
                "email": "test_user1@example.com",
                "username": "test_user1",
                "password": "test_password1",
                "first_name": "test_user1_first_name",
                "last_name": "test_user1_last_name",
                "gender": "Female",
                "year": "2nd year",
                "mobile": "9411123411",
                "college_name": "IIT BHU",
                "referral_code": "",
            },
        )
        self.assertEqual(response.status_code, 409)

    # Valid arguments (uidb64, token)
    def test_activate_account_view_GET_200(self):
        response = self.client.get(self.activate_account_url1)
        self.assertEqual(response.status_code, 200)

    # Invalid arguments (uidb64, token)
    def test_activate_account_view_GET_401(self):
        response = self.client.get(self.activate_account_url2)
        self.assertEqual(response.status_code, 401)

    # Password reset: email is valid and user is active
    def test_password_reset_email_view_POST_200(self):
        self.client.get(self.activate_account_url1)
        response = self.client.post(
            self.password_reset_email_url, {"email": "test_user1@example.com"}
        )
        self.assertEqual(response.status_code, 200)

    # Password reset: email is valid and user is not active
    def test_password_reset_email_view_POST_401(self):
        response = self.client.post(
            self.password_reset_email_url, {"email": "test_user1@example.com"}
        )
        self.assertEqual(response.status_code, 401)

    # Password reset: email is invalid
    def test_password_reset_email_view_POST_400(self):
        response = self.client.post(
            self.password_reset_email_url, {"email": "test_us@example.com"}
        )
        self.assertEqual(response.status_code, 400)

    # Valid arguments (uidb64, token)
    def test_password_token_check_view_GET_200(self):
        response = self.client.get(self.password_reset_confirm_url1)
        self.assertEqual(response.status_code, 200)

    # invalid arguments (uidb64, token)
    def test_password_token_check_view_GET_401(self):
        response = self.client.get(self.password_reset_confirm_url2)
        self.assertEqual(response.status_code, 401)

    # Valid arguments (uidb64, token)
    def test_new_password_successfully_set(self):
        response = self.client.patch(
            reverse("password-reset-complete"),
            {"password": "NewPassword123", "token": self.token, "uidb64": self.uidb64},
        )
        self.assertEqual(response.status_code, 200)

    # Invalid arguments (uidb64, token)
    def test_new_password_not_set_401(self):
        response = self.client.patch(
            reverse("password-reset-complete"),
            {
                "password": "NewPassword123",
                "token": "some-token",
                "uidb64": self.uidb64,
            },
        )
        self.assertEqual(response.status_code, 401)
        response = self.client.patch(
            reverse("password-reset-complete"),
            {
                "password": "NewPassword123",
                "token": self.token,
                "uidb64": "some-uidb64",
            },
        )
        self.assertEqual(response.status_code, 401)

    # No arguments passed
    def test_new_password_not_set_400(self):
        response = self.client.patch(reverse("password-reset-complete"))
        self.assertEqual(response.status_code, 400)

    # User update get data
    def test_update_view_get(self):
        self.client.force_authenticate(user=self.test_user1)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)

    # User update by post data
    def test_update_view_post(self):
        self.client.force_authenticate(user=self.test_user1)
        response = self.client.post(
            self.update_url,
            {"last_name": "test_user1_last_name_update", "mobile": "9876543210"},
        )
        self.assertEqual(response.status_code, 200)
