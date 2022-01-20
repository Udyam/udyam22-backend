from rest_framework import generics, status
from rest_framework.response import Response
import xlwt
from .serializers import QuerySerializer
from custom_auth.models import UserAccount
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import Http404


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
