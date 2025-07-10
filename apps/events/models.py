from typing import Tuple
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

# Assuming CustomUser is imported from apps.users.models
# If not available, use AbstractUser as fallback
from apps.users.models import CustomUser


class EventManager(models.Manager):
    """Custom manager for an Event model with type-safe query methods."""

    def past(self) -> QuerySet["Event"]:
        """
        Return events that have already happened.
        Returns:
            QuerySet: Events with dates before today.
        """
        return self.filter(date__lt=timezone.now().date())

    def published(self) -> QuerySet["Event"]:
        """
        Return only published events (upcoming).
        Returns:
            QuerySet: Events with 'published' status.
        """
        return self.filter(status="published")

    def filter_by_creator(self, user) -> QuerySet["Event"]:
        """
        Filter events by creator.
        Args:
            user: The user who created the events.
        Returns:
            QuerySet: Events created by the specified user.
        """
        return self.filter(created_by=user)


class Event(models.Model):
    """
    Model representing an event with comprehensive validation and status management.

    This model handles event creation, validation, status transitions,
    and registration management with proper permission checks.
    """

    STATUS_CHOICES: tuple[tuple[str, str], ...] = (
        ("published", "Published"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    title: models.CharField = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(3, message="Title must be at least 3 characters long.")
        ],
    )
    description: models.TextField = models.TextField(
        max_length=1000,
        blank=False,
        null=False,
    )
    image: models.ImageField = models.ImageField(
        upload_to="event_images/",
        blank=True,
        null=True,
    )
    location: models.CharField = models.CharField(
        max_length=200,
        blank=False,
        null=False,
    )
    date: models.DateField = models.DateField(
        blank=False,
        null=False,
    )
    start_time: models.TimeField = models.TimeField(
        blank=False,
        null=False,
    )
    status: models.CharField = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        choices=STATUS_CHOICES,
        default="published",
    )
    created_by: models.ForeignKey = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="created_events",
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    objects = EventManager()

    class Meta:
        """
        Meta configuration for an Event model.

        Orders events by date and start time.
        Adds indexes for faster filtering by date, status, and creator.
        """

        ordering = ["date", "start_time"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self) -> str:
        """
        String representation of the event.
        Returns:
            str: Formatted string with title, date, and status.
        """
        return f"{self.title} - {self.date} ({self.status})"

    def clean(self) -> None:
        """
        Perform custom event validation for the Event model.
        Validates: Creator permissions, Text field content
        Date and status consistency
        Raises:
            PermissionDenied: If user doesn't have creator permissions.
            ValidationError: If validation fails.
        """
        super().clean()

        # Check creator permissions
        if not hasattr(self.created_by, "is_creator") or not self.created_by.is_creator:
            raise PermissionDenied("Only users with role 'creator' can create events.")

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

    def save(self, *args, **kwargs) -> None:
        """
        Override save method to enforce logic and handle event status updates.
        Performs full validation before saving and handles status change cascades.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Validate before saving
        self.full_clean()

        # If event is not cancelled, update status according to date
        if self.status != "cancelled":
            if self.is_past:
                self.status = "completed"
            elif self.is_upcoming:
                self.status = "published"

        # Get previous status for comparison
        previous_status = None
        if self.pk:
            previous_status = Event.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        # Handle cascading status changes
        if previous_status != "cancelled" and self.status == "cancelled":
            self._cancel_all_registrations()

    def cancel_event(self, user) -> None:
        """
        Cancel own event. Allow only the creator to cancel.
        Cancel all active registrations for this event.
        Args:
            user: The user attempting to cancel the event.
        Raises:
            PermissionError: If user is not the event creator.
            ValueError: If event cannot be cancelled.
        """

        if self.created_by != user:
            raise PermissionError("Only the event creator can cancel this event.")
        if self.status == "cancelled":
            raise ValueError("Event is already cancelled.")
        if self.status != "published":
            raise ValueError("Only published events can be cancelled.")

        self.status = "cancelled"
        self.save()

    def _cancel_all_registrations(self) -> None:
        """
        Cancel all active registrations for cancelled event.
        Private method to handle registration cancellation when an event is cancelled.
        """
        active_regs = self.registrations.filter(status="registered")  # type: ignore
        print(f"Cancelling {active_regs.count()} registrations for event {self.id}")  # type: ignore
        active_regs.update(status="cancelled", updated_at=timezone.now())

    def can_register(self, user) -> Tuple[bool, str]:
        """
        Check if a user can register for this event.
        Args:
            user: The user attempting to register.
        Returns:
            Tuple[bool, str]: (can_register, reason) where can_register is True
            if registration is allowed, and reason explains why.
        """
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
        if self.registrations.filter(user=user, status="registered").exists():  # type: ignore
            return False, "Already registered for this event."

        return True, "Can register."

    @property
    def is_upcoming(self) -> bool:
        """
        Check if event is in the future.
        Returns:
            bool: True if event date is today or in the future.
        """
        return self.date >= timezone.now().date()

    @property
    def is_past(self) -> bool:
        """
        Check if event is in the past.
        Returns:
            bool: True if event date is before today.
        """
        return self.date < timezone.now().date()

    @property
    def registration_count(self) -> int:
        """
        Return number of current active registrations.
        Returns:
            int: Count of active registrations for this event.
        """
        return self.registrations.filter(status="registered").count()  # type: ignore

    @property
    def can_be_cancelled(self) -> bool:
        """
        Check if event can be cancelled.
        Returns:
            bool: True if event status is 'published'.
        """
        return self.status == "published"

    @property
    def is_cancelled(self) -> bool:
        """
        Check if event is cancelled.
        Returns:
            bool: True if event status is 'cancelled'.
        """
        return self.status == "cancelled"


class EventRegistration(models.Model):
    """
    Model representing user registration for an event.

    Handles user registration lifecycle including validation,
    cancellation, and status management.
    """

    STATUS_CHOICES: tuple[tuple[str, str], ...] = (
        ("registered", "Registered"),
        ("cancelled", "Cancelled"),
    )

    user: models.ForeignKey = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    event: models.ForeignKey = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",  # MyPy can't see that
    )
    status: models.CharField = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="registered",
    )
    registered_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta configuration for EventRegistration model.

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
        """
        String representation of the registration.
        Returns:
            str: Formatted string with user email and event title.
        """
        user_identifier = getattr(self.user, "email", str(self.user))
        return f"{user_identifier} - {self.event.title}"

    def clean(self):
        """
        Perform custom validation for a registration model.
        Validates registration eligibility and cancellation permissions.
        Raises:
            ValidationError: If validation fails.
        """
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

    def save(self, *args, **kwargs) -> None:
        """
        Ensure validation is always performed before saving.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def can_cancel(self):
        """
        Check if registration can be cancelled.
        Returns:
            bool: True if registration is active and event allows cancellation.
        """
        return (
            self.status == "registered"
            and self.event.status == "published"
            and self.event.is_upcoming
        )

    def cancel_registration(self) -> None:
        """
        Cancel the registration.
        Raises:
        ValueError: If registration cannot be cancelled.
        """
        if not self.can_cancel():
            raise ValueError("Cannot cancel this registration.")

        self.status = "cancelled"
        self.save()
