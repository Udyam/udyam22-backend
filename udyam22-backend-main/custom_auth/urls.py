from django.urls import path
from .views import (
    RequestPasswordResetEmail,
    PasswordTokenCheckView,
    NewPasswordView,
    RegisterView,
)
from .views import ActivateAccountView, LoginView, LogoutView, UserUpdateView

"""
TODO:
Add the urlpatterns of the endpoints, required for implementing
Todo GET (List and Detail), PUT, PATCH and DELETE.
"""

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("update/", UserUpdateView.as_view(), name="update"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate-account",
    ),
    path(
        "password_reset/email/",
        RequestPasswordResetEmail.as_view(),
        name="password-reset-email",
    ),
    path(
        "password_reset/<uidb64>/<token>/",
        PasswordTokenCheckView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password_reset/update_password/",
        NewPasswordView.as_view(),
        name="password-reset-complete",
    ),
]
