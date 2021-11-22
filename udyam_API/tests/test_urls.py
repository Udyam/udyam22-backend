from django.test import SimpleTestCase
from django.urls import reverse, resolve
from udyam_API.views import WorkshopView, GetAllNoticeView, GetNoticeByIdView


class TestUrls(SimpleTestCase):
    def test_workshop_url(self):
        workshop_url = reverse("workshop")
        self.assertEqual(resolve(workshop_url).func.view_class, WorkshopView)

    def test_get_all_notice_url(self):
        get_all_notice_url = reverse("get-all-notice")
        self.assertEqual(resolve(get_all_notice_url).func.view_class, GetAllNoticeView)

    def test_get_notice_by_id_url(self):
        get_notice_by_id_url = reverse("get-notice-by-id", args=["123"])
        self.assertEqual(resolve(get_notice_by_id_url).func.view_class, GetNoticeByIdView)
