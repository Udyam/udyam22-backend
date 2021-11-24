from django.shortcuts import get_object_or_404, render
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
