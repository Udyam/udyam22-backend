from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import QuerySerializer
from custom_auth.models import UserAccount
from rest_framework.views import APIView


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
