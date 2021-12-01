from django.db import models


class Event(models.Model):
    eventname = models.CharField(max_length=20, unique=True)
    members_from_1st_year = models.IntegerField()
    members_after_1st_year = models.IntegerField()

    def __str__(self):
        return self.eventname


class Workshop(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    url = models.URLField(max_length=200)

    def __str__(self):
        string = str(self.event) + ', ' + str(self.date)
        return string


class NoticeBoard(models.Model):
    title = models.TextField(blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    date = models.DateField(auto_now=True)

    def str(self):
        return f"{self.title}"
