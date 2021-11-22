from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Workshop, Event, NoticeBoard
from .serializers import WorkshopSerializer, NoticeBoardSerializer


class WorkshopView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkshopSerializer

    def get(self, request):
        response_body = []
        workshops = Workshop.objects.all()
        serializer = WorkshopSerializer(workshops, many=True)
        for w in serializer.data:
            workshop = Workshop.objects.get(id=w['id'])
            event = Event.objects.get(id=w['event'])
            event_name = event.eventname
            response_body.append({
                "id": workshop.id,
                "date": workshop.date,
                "time": workshop.time,
                "url": workshop.url,
                "event": event_name,
            })

        return Response(response_body, status=status.HTTP_200_OK)


class GetAllNoticeView(generics.GenericAPIView):
    serializer_class = NoticeBoardSerializer

    def get(self, request):
        response_body = []
        all_notice = NoticeBoard.objects.all()
        serializer = NoticeBoardSerializer(all_notice, many=True)
        for notice in serializer.data:
            response_body.append(notice)

        return Response(response_body, status=status.HTTP_200_OK)


class GetNoticeByIdView(generics.GenericAPIView):
    serializer_class = NoticeBoardSerializer

    def get(self, request, id):
        try:
            notice = NoticeBoard.objects.get(id=id)
            serializer = NoticeBoardSerializer(notice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Notice with the given id doesn't exist!"}, status=status.HTTP_404_NOT_FOUND)
