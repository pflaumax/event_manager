from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from apps.users.models import CustomUser


class EventManager(models.Manager):
    """Custom manager for Event model."""

    def upcoming(self):
        """Return events that haven't started yet."""
        return self.filter(date__gte=timezone.now().date())

    def past(self):
        """Return events that have already happened."""
        return self.filter(date__lt=timezone.now().date())

    def filter_by_creator(self, user):
        return self.filter(created_by=user)


class Event(models.Model):
    """Model representing an event."""

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    )

    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    description = models.TextField(
        max_length=1000, help_text="Detailed description of the event"
    )
    location = models.CharField(max_length=200, help_text="Event venue or address")
    date = models.DateField(help_text="Event date")
    start_time = models.TimeField(help_text="Event start time")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.date}"


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
