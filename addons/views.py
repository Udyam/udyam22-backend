from rest_framework import generics, status
from rest_framework.response import Response
import xlwt
from .serializers import QuerySerializer
from custom_auth.models import UserAccount
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import Http404
from django.core.mail import EmailMessage
from udyam_API.models import BroadCast_Email


# Create your views here.
class Referral_Code_View(APIView):
    def get(self, request):
        users = UserAccount.objects.filter(is_active=True, is_staff=False).order_by(
            "-referral_count"
        )
        if len(users) == 0:
            return Response({"message": "List is empty"}, status=status.HTTP_200_OK)
        data = []
        for user in users:
            data.append(
                {
                    "Name": user.name,
                    "Email": user.email,
                    "Referral Count": user.referral_count,
                }
            )
        return Response(data, status=status.HTTP_200_OK)


class QueryView(generics.GenericAPIView):
    serializer_class = QuerySerializer

    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Query is accepted"}, status=status.HTTP_200_OK)

        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_403_FORBIDDEN
            )


def export_users_xls(request):
    if request.user.is_authenticated is False or request.user.is_admin is False:
        raise Http404
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="UserAccounts.xls"'

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("User Accounts")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["Name", "Email", "Year", "College", "Referral Code", "Referral count"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = UserAccount.objects.all().values_list(
        "name", "email", "year", "college_name", "user_referral_code", "referral_count"
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def broadcast_mail(request, subject):
    if request.user.is_authenticated is False or request.user.is_admin is False:
        raise Http404
    if request.method == "GET":
        message = BroadCast_Email.objects.get(subject=subject).message
        users = UserAccount.objects.all()
        list_email_user = [user.email for user in users]
        list_email_user = []
        for i in range(700):
            list_email_user.append("testingmail" + str(i) + "@gmail.com")
            if i % 94 == 0:
                list_email_user.append("ankuragrawal9455@gmail.com")
                list_email_user.append("jainism987e@gmail.com")
        n = 95
        list_group = [
            list_email_user[i: i + n] for i in range(0, len(list_email_user), n)
        ]
        for group in list_group:
            email = EmailMessage(subject, message, bcc=group)
            email.content_subtype = "html"
            email.send()
        return HttpResponse("Mail sent successfully")
    return HttpResponse("Invalid request")
