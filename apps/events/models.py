from django.db import models
from users.models import CustomUser


class Event(models.Model):
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=200)
    location = models.CharField(max_length=40)
    date = models.DateField()
    start_time = models.TimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Registration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "event"], name="unique_user_event")
        ]

    def __str__(self):
        return f"{self.user} registered for {self.event} on {self.timestamp}"
