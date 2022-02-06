from django.urls import path
from .views import QueryView, Referral_Code_View, export_users_xls, broadcast_mail

urlpatterns = [
    path("query/", QueryView.as_view(), name="query"),
    path("referrals/", Referral_Code_View.as_view(), name="referral"),
    path("export/xls/", export_users_xls, name="export_users_xls"),
    path("broadcast/<subject>/", broadcast_mail, name="broadcast_mail"),
]
