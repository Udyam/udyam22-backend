from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Workshop, NoticeBoard
from .serializers import WorkshopSerializer, NoticeBoardSerializer


class WorkshopView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkshopSerializer

    def list(self, request):
        workshops = Workshop.objects.all().order_by('-date')
        serializer = WorkshopSerializer(workshops, many=True)

        return Response(serializer.data)


class GetAllNoticeView(generics.ListAPIView):
    serializer_class = NoticeBoardSerializer

    def list(self, request):
        all_notice = NoticeBoard.objects.all().order_by('-date')
        serializer = NoticeBoardSerializer(all_notice, many=True)

        return Response(serializer.data)


class GetNoticeByIdView(generics.RetrieveAPIView):
    serializer_class = NoticeBoardSerializer

    def retrieve(self, request, id):
        all_notice = NoticeBoard.objects.all()
        notice = get_object_or_404(all_notice, pk=id)
        serializer = NoticeBoardSerializer(notice)

        return Response(serializer.data)
