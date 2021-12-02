from rest_framework import serializers
from .models import Workshop, Team, NoticeBoard


class WorkshopSerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField()

    class Meta:
        model = Workshop
        fields = "__all__"


class NoticeBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeBoard
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        data = self.validated_data
        teamname = data["teamname"]
        event = data["event"]
        leader = data["leader"]
        member1 = data["member1"]
        member2 = data["member2"]
        team = Team.objects.create(
            teamname=teamname,
            event=event,
            leader=leader,
            member1=member1,
            member2=member2,
        )
        return team

    class Meta:
        model = Team
        fields = ["teamname", "event", "leader", "member1", "member2"]


class TeamSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["teamname", "event", "submission"]
