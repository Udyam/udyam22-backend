from django.urls import path
from .views import QueryView, Referral_Code_View

urlpatterns = [
    path("query/", QueryView.as_view(), name="query"),
    path("referrals/", Referral_Code_View.as_view(), name="referral"),
]
