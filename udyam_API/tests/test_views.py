from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from custom_auth.models import UserAccount
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.authtoken.models import Token
from udyam_API.models import NoticeBoard


class TestView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.credentials_user1 = {
            "email": "test_user1@example.com",
            "password": "test_password1",
        }
        self.test_user1 = UserAccount.objects.create_user(
            **self.credentials_user1)
        self.test_user1.name = "test_user1_name"
        self.test_user1.year = "2nd year"
        self.test_user1.college_name = "IIT BHU"
        self.test_user1.save()

        self.auth_token = Token.objects.get_or_create(user=self.test_user1)
        self.uidb64 = urlsafe_base64_encode(smart_bytes(self.test_user1.id))
        self.token = PasswordResetTokenGenerator().make_token(self.test_user1)

        self.notice1_data = {
            "title": "notice1",
            "description": "notice1_description",
        }
        self.notice1 = NoticeBoard.objects.create(**self.notice1_data)
        self.id = self.notice1.id

        self.workshop_url = reverse("workshop")
        self.get_all_notice_url = reverse("get-all-notice")
        self.get_notice_by_id_url1 = reverse("get-notice-by-id", args=[self.id])
        self.get_notice_by_id_url2 = reverse("get-notice-by-id", args=["123"])

    # get data from WorkshopView
    def test_workshop_view_get(self):
        self.client.force_authenticate(user=self.test_user1)
        response = self.client.get(self.workshop_url)
        self.assertEqual(response.status_code, 200)

    def test_get_all_notice_view(self):
        response = self.client.get(self.get_all_notice_url)
        self.assertEqual(response.status_code, 200)

    def test_get_notice_by_id_view_200(self):
        response = self.client.get(self.get_notice_by_id_url1)
        self.assertEqual(response.status_code, 200)

    def test_get_notice_by_id_view_404(self):
        response = self.client.get(self.get_notice_by_id_url2)
        self.assertEqual(response.status_code, 404)
