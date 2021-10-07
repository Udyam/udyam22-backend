from django.urls import path
from .views import RequestPasswordResetEmail, PasswordTokenCheckView, NewPasswordView,RegisterView
from .views import ActivateAccountView,LoginView,LogoutView

"""
TODO:
Add the urlpatterns of the endpoints, required for implementing
Todo GET (List and Detail), PUT, PATCH and DELETE.
"""

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', RegisterView.as_view()),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(),name="activate-account"),
    path('password_reset/email/', RequestPasswordResetEmail.as_view(), name='password-reset-email'),
    path('password_reset/<uidb64>/<token>/', PasswordTokenCheckView.as_view(), name='password-reset-confirm'),
    path('password_reset/update_password/', NewPasswordView.as_view(), name='password-reset-complete'),
]