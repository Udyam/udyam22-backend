from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Event, Workshop, Team, NoticeBoard
from .serializers import (
    EventSerializer,
    WorkshopSerializer,
    TeamSerializer,
    TeamSubmissionSerializer,
    NoticeBoardSerializer,
)
from custom_auth.models import UserAccount
from custom_auth.utils import Util, part1, part2, part3, part4, part5


def checks(request):
    try:
        event = Event.objects.get(eventname=request.data["event"])
        leader = UserAccount.objects.get(email=request.data["leader"])
        member1 = (
            UserAccount.objects.get(email=request.data["member1"])
            if request.data["member1"]
            else None
        )
        member2 = (
            UserAccount.objects.get(email=request.data["member2"])
            if request.data["member2"]
            else None
        )
        event_teams = Team.objects.filter(event=event)
        first_yearites = 0
        second_yearites = 0
        if leader.year == "ONE":
            first_yearites += 1
        else:
            second_yearites += 1
        if member1:
            if member1.year == "ONE":
                first_yearites += 1
            else:
                second_yearites += 1
        if member2:
            if member2.year == "ONE":
                first_yearites += 1
            else:
                second_yearites += 1
    except Event.DoesNotExist:
        return "Event does not exist"
    except UserAccount.DoesNotExist:
        return "User does not exist"

    if (
        request.data["leader"] == request.data["member1"]
        or request.data["leader"] == request.data["member2"]
        or (
            request.data["member1"] == request.data["member2"]
            and request.data["member1"] != ""
        )
    ):
        return "Single user cannot be present twice in the team"
    elif leader != request.user and member1 != request.user and member2 != request.user:
        return "Requesting user must be a member of the team. Cannot create a team which you are not a part of."
    elif Team.objects.filter(teamname=request.data["teamname"], event=event).count():
        return "Team name already taken"
    elif (
        event_teams.filter(leader=leader).count()
        or event_teams.filter(member1=leader).count()
        or event_teams.filter(member2=leader).count()
    ):
        return "Leader already has a team in this event"
    elif (
        event_teams.filter(leader=member1).count()
        or event_teams.filter(member1=member1).count()
        or event_teams.filter(member2=member1).count()
    ) and member1 is not None:
        return "Member 1 already has a team in this event"
    elif (
        event_teams.filter(leader=member2).count()
        or event_teams.filter(member1=member2).count()
        or event_teams.filter(member2=member2).count()
    ) and member2 is not None:
        return "Member 2 already has a team in this event"
    elif (
        second_yearites != 0
        and first_yearites + second_yearites > event.members_after_1st_year
    ):
        return (
            "Max size of a not-all-1st-yearites team is "
            + str(event.members_after_1st_year)
            + " for this event"
        )
    elif second_yearites == 0 and first_yearites > event.members_from_1st_year:
        return (
            "Max size of a all-1st-yearites team is "
            + str(event.members_from_1st_year)
            + " for this event"
        )


class GetAllEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class WorkshopView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WorkshopSerializer
    queryset = Workshop.objects.all().order_by("-date")


class GetAllNoticeView(generics.ListAPIView):
    serializer_class = NoticeBoardSerializer
    queryset = NoticeBoard.objects.all().order_by("-date")


class GetNoticeByIdView(generics.RetrieveAPIView):
    serializer_class = NoticeBoardSerializer
    queryset = NoticeBoard.objects.all()
    lookup_field = "id"


class TeamCreateView(generics.GenericAPIView):
    """
    Create a new team. Requires token in the Authorization header.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TeamSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = checks(request)
        if message:
            return Response({"error": message}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        team = Team.objects.get(
            teamname=request.data["teamname"],
            event=Event.objects.get(eventname=request.data["event"]),
        )
        team_info = {
            "teamname": team.teamname,
            "event": team.event.eventname,
            "leader": team.leader.email,
            "member1": team.member1.email if team.member1 else None,
            "member2": team.member2.email if team.member2 else None,
        }
        email_body = (
            part1
            + "team "
            + team.teamname
            + part2
            + "You are successfully registered for the event "
            + team.event.eventname
            + ". Please join the Discord server via below link:"
            + part3
            + "https://discord.gg/gNrEW8vp4G"
            + part4
            + "Discord link"
            + part5
        )
        data = {
            "email_body": email_body,
            "to_mail": [team.leader.email],
            "email_subject": "Link to join Discord server",
        }
        if team.member1:
            data["to_mail"].append(team.member1.email)
        if team.member2:
            data["to_mail"].append(team.member2.email)

        Util.send_email(data)
        return Response(team_info, status=status.HTTP_200_OK)


class TeamGetUserView(generics.ListAPIView):
    """
    Get all the teams of the logged in user. Requires token in the Authorization header.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TeamSerializer

    def appendTeam(self, teams, event_teams):
        for team in teams:
            team_info = {
                "id": team.id,
                "teamname": team.teamname,
                "event": team.event.eventname,
                "leader": team.leader.email,
                "member1": team.member1.email if team.member1 else None,
                "member2": team.member2.email if team.member2 else None,
            }
            event_teams.append(team_info)

    def get(self, request):
        try:
            teams_as_leader = Team.objects.filter(leader=request.user)
            teams_as_member1 = Team.objects.filter(member1=request.user)
            teams_as_member2 = Team.objects.filter(member2=request.user)
            event_teams = []
            self.appendTeam(teams_as_leader, event_teams)
            self.appendTeam(teams_as_member1, event_teams)
            self.appendTeam(teams_as_member2, event_teams)
            return Response(event_teams, status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "No such user exists"}, status=status.HTTP_404_NOT_FOUND
            )


class TeamView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TeamSerializer

    def teamInfo(self, team):
        team_info = {
            "teamname": team.teamname,
            "event": team.event.eventname,
            "leader": team.leader.email,
            "member1": team.member1.email if team.member1 else None,
            "member2": team.member2.email if team.member2 else None,
        }
        return team_info

    def get(self, request, id):
        try:
            team = Team.objects.get(id=id)
            return Response(self.teamInfo(team), status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response(
                {"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, id):
        try:
            team = Team.objects.get(id=id)
            event = Event.objects.get(eventname=request.data["event"])
            leader = UserAccount.objects.get(email=request.data["leader"])
            team.teamname = request.data["teamname"]
            team.event = event
            team.leader = leader
            team.member1 = (
                UserAccount.objects.get(email=request.data["member1"])
                if request.data["member1"] != ""
                else None
            )
            team.member2 = (
                UserAccount.objects.get(email=request.data["member2"])
                if request.data["member2"] != ""
                else None
            )
            message = checks(request)
            if message and message != "Team name already taken":
                return Response({"error": message}, status=status.HTTP_403_FORBIDDEN)
            team.save()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(self.teamInfo(team), status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response(
                {"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "User account not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, id):
        if Team.objects.filter(id=id).count():
            team = Team.objects.get(id=id)
            if (
                request.user == team.leader
                or request.user == team.member1
                or request.user == team.member2
            ):
                team.delete()
                return Response(
                    {"message": "Team deleted successfully"}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Only a team member is allowed to delete his/her team."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)


class TeamSubmissionView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TeamSubmissionSerializer

    def post(self, request):
        team = Team.objects.get(
            teamname=request.data["teamname"],
            event=Event.objects.get(eventname=request.data["event"]),
        )
        if team is None:
            return Response(
                {"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if team.leader != request.user:
            return Response(
                {"error": "Only the team leader is allowed to submit."},
                status=status.HTTP_403_FORBIDDEN,
            )
        team.submission = request.data["submission"]
        team.save()
        return Response(
            {"message": "Submitted successfully"}, status=status.HTTP_200_OK
        )

class TeamCountView(generics.GenericAPIView):
    serializer_class = TeamSubmissionSerializer
    def get(self, request):
        res = {}
        for event in Event.objects.all():
            teams = Team.objects.filter(event=event)
            res[event.eventname] = teams.count()
        return Response(
            res, status=status.HTTP_200_OK
        )
