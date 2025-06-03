from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from apps.users.models import CustomUser


class EventManager(models.Manager):
    """Custom manager for Event model."""

    def past(self):
        """Return events that have already happened."""
        return self.filter(date__lt=timezone.now().date())

    def published(self):
        """Return only published events (upcoming)."""
        return self.filter(status="published")

    def filter_by_creator(self, user):
        """Filter events by creator."""
        return self.filter(created_by=user)


class Event(models.Model):
    """Model representing an event."""

    STATUS_CHOICES = (
        ("published", "Published"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(3, message="Title must be at least 3 characters long.")
        ],
    )
    description = models.TextField(
        max_length=1000,
        blank=False,
        null=False,
        help_text="Detailed description of the event.",
    )
    location = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        help_text="Event venue or address.",
    )
    date = models.DateField(
        blank=False,
        null=False,
        help_text="Event date.",
    )
    start_time = models.TimeField(
        blank=False,
        null=False,
        help_text="Event start time.",
    )
    status = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        choices=STATUS_CHOICES,
        default="published",
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EventManager()

    class Meta:
        """
        Orders events by date and start time.
        Adds indexes for faster filtering by date, status, and creator
        """

        ordering = ["date", "start_time"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        """String representation."""
        return f"{self.title} - {self.date} ({self.status})"

    def clean(self):
        """Perform custom event validation for the Event model."""
        super().clean()

        # Check creator permissions
        if not self.created_by.is_creator:
            raise PermissionError("Only users with role 'creator' can create events.")

        # Clean and validate text fields
        for field in ["title", "description", "location"]:
            value = (getattr(self, field) or "").strip()
            setattr(self, field, value)

            if not any(c.isalnum() for c in value):
                raise ValidationError(
                    {
                        field: f"{field.capitalize()} must contain at least one letter or number."
                    }
                )

        # Auto-update status for past events
        if self.date:
            current_date = timezone.now().date()

            if self.date < current_date and self.status == "published":
                self.status = "completed"

            if self.date < current_date and self.status not in [
                "completed",
                "cancelled",
            ]:
                raise ValidationError(
                    {
                        "date": "Event date cannot be in the past unless status is 'completed' or 'cancelled'."
                    }
                )

    def save(self, *args, **kwargs):
        """
        Override save method to enforce logic and handle event status updates.
        """
        # Validate before saving
        self.full_clean()

        # Get previous status for comparison
        previous_status = None
        if self.pk:
            previous_status = Event.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        # Handle cascading status changes
        if previous_status != "cancelled" and self.status == "cancelled":
            self._cancel_all_registrations()

    def cancel_event(self, user):
        """Allow only the creator to cancel the event."""
        if self.created_by != user:
            raise PermissionError("Only the event creator can cancel this event.")
        if self.status == "cancelled":
            raise ValueError("Event is already cancelled.")
        if self.status != "published":
            raise ValueError("Only published events can be cancelled.")

        self.status = "cancelled"
        self.save()

    def can_register(self, user):
        """Check if a user can register for this event."""
        # Check user permissions
        if not user.is_authenticated:
            return False, "User must be logged in to register."
        if not user.can_register_for_events():
            return False, "Only visitors can register for events."

        # Check event status and timing
        if not self.is_upcoming:
            return False, "Cannot register for past events."
        if self.status != "published":
            return False, "Event is not available for registration."

        # Check existing registration
        if self.registrations.filter(user=user, status="registered").exists():
            return False, "Already registered for this event."

        return True, "Can register."

    def _cancel_all_registrations(self):
        """Cancel all active registrations for this event."""
        self.registrations.filter(status="registered").update(
            status="cancelled", updated_at=timezone.now()
        )

    @property
    def is_upcoming(self):
        """Check if event is in the future."""
        return self.date >= timezone.now().date()

    @property
    def is_past(self):
        """Check if event is in the past."""
        return self.date < timezone.now().date()

    @property
    def registration_count(self):
        """Return number of current active registrations."""
        return self.registrations.filter(status="registered").count()

    @property
    def can_be_cancelled(self):
        """Check if event can be cancelled."""
        return self.status == "published"


class EventRegistration(models.Model):
    """Model representing user registration for an event."""

    STATUS_CHOICES = (
        ("registered", "Registered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="registered",
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Adds constraints for each user can only register once per event.
        Adds indexes for faster filtering by user-status and event-status.
        """

        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_registration",
            )
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["event", "status"]),
        ]
        ordering = ["-registered_at"]

    def __str__(self):
        """String representation."""
        return f"{self.user.username} - {self.event.title} ({self.status})"

    def clean(self):
        """Perform custom validation for registration model."""
        super().clean()

        # Validate new registrations or status changes to registered
        if self.pk is None or self.status == "registered":
            can_register, reason = self.event.can_register(self.user)
            if not can_register:
                raise ValidationError(reason)

        # Validate cancellation
        if self.status == "cancelled" and self.pk:
            try:
                original = EventRegistration.objects.get(pk=self.pk)
                if original.status != "registered":
                    raise ValidationError("Can only cancel active registrations.")
                if not original.can_cancel():
                    raise ValidationError("Cannot cancel this registration.")
            except EventRegistration.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        """Ensure validation is always performed before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def can_cancel(self):
        """Check if registration can be cancelled."""
        return (
            self.status == "registered"
            and self.event.status == "published"
            and self.event.is_upcoming
        )

    def cancel_registration(self):
        """Cancel the registration."""
        if not self.can_cancel():
            raise ValueError("Cannot cancel this registration.")

        self.status = "cancelled"
        self.save()
