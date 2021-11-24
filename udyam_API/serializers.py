from rest_framework import serializers
from .models import Workshop, NoticeBoard


class WorkshopSerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField()

    class Meta:
        model = Workshop
        fields = "__all__"


class NoticeBoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoticeBoard
        fields = "__all__"
