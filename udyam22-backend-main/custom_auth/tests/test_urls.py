from django.test import SimpleTestCase
from django.urls import reverse, resolve
from custom_auth.views import (
    LoginView,
    LogoutView,
    UserUpdateView,
    RegisterView,
    ActivateAccountView,
    RequestPasswordResetEmail,
    PasswordTokenCheckView,
    NewPasswordView,
)


class TestUrls(SimpleTestCase):
    def test_login_url(self):
        login_url = reverse("login")
        self.assertEqual(resolve(login_url).func.view_class, LoginView)

    def test_logut_url(self):
        logout_url = reverse("logout")
        self.assertEqual(resolve(logout_url).func.view_class, LogoutView)

    def test_update_url(self):
        update_url = reverse("update")
        self.assertEqual(resolve(update_url).func.view_class, UserUpdateView)

    def test_register_url_is_resolved(self):
        register_url = reverse("register")
        self.assertEqual(resolve(register_url).func.view_class, RegisterView)

    def test_activate_account_url_is_resolved(self):
        activate_account_url = reverse(
            "activate-account", args=["some-uidb64", "some-token"]
        )
        self.assertEqual(
            resolve(activate_account_url).func.view_class, ActivateAccountView
        )

    def test_password_reset_email_url_is_resolved(self):
        password_reset_email_url = reverse("password-reset-email")
        self.assertEqual(
            resolve(password_reset_email_url).func.view_class, RequestPasswordResetEmail
        )

    def test_password_reset_confirm_url_is_resolved(self):
        password_reset_confirm_url = reverse(
            "password-reset-confirm", args=["some-uidb64", "some-token"]
        )
        self.assertEqual(
            resolve(password_reset_confirm_url).func.view_class, PasswordTokenCheckView
        )

    def test_password_reset_complete_url_is_resolved(self):
        password_reset_complete_url = reverse("password-reset-complete")
        self.assertEqual(
            resolve(password_reset_complete_url).func.view_class, NewPasswordView
        )
