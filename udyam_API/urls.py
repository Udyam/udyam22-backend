from django.urls import path
from .views import WorkshopView, GetAllNoticeView, GetNoticeByIdView


urlpatterns = [
    path("workshop/", WorkshopView.as_view(), name="workshop"),
    path('get_all_notice/', GetAllNoticeView.as_view(), name='get-all-notice'),
    path('get_notice_by_id/<int:id>', GetNoticeByIdView.as_view(), name='get-notice-by-id'),
]
