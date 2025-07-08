from typing import Any
from django import forms
from django.core.exceptions import PermissionDenied
from .models import Event


class EventForm(forms.ModelForm):
    """
    A form for creating or editing events.
    This form handles the creation and editing of Event instances
    with custom widgets and validation logic.
    Attributes:
        user: Optional User instance passed from the view for validation purposes.
    """

    class Meta:
        """Meta configuration for the EventForm."""

        model: type[Event] = Event
        fields: tuple[str, ...] = (
            "title",
            "image",
            "description",
            "location",
            "date",
            "start_time",
        )

        widgets: dict[str, forms.Widget] = {
            "title": forms.TextInput(
                attrs={"placeholder": "Must be at least 3 characters long"}
            ),
            "description": forms.Textarea(
                attrs={"placeholder": "Detailed description of the event"}
            ),
            "location": forms.TextInput(
                attrs={"placeholder": "Event venue or address"}
            ),
            "date": forms.DateInput(attrs={"placeholder": "YYYY-MM-DD"}),
            "start_time": forms.TimeInput(attrs={"placeholder": "HH:MM"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the form and optionally store the user passed from the view.
        Args:
            *args: Variable length argument list passed to parent class.
            **kwargs: Arbitrary keyword arguments. 'User' key is extracted if present for use in validation.
        """

        self.user = kwargs.pop("user", None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Perform custom validation before model's clean() is called.
        Ensures the user has 'creator' role before proceeding.
        """
        if not self.user or not getattr(self.user, "is_creator", False):
            raise PermissionDenied("Only users with role 'creator' can create events.")

        # Assign the user to the instance before model validation
        if self.instance and not self.instance.pk:
            self.instance.created_by = self.user

        return super().clean()

    def save(self, commit=True):
        """
        Save the event with created_by set if not already saved.
        """
        event = super().save(commit=False)
        if self.user and not event.created_by_id:
            event.created_by = self.user
        if commit:
            event.save()
        return event
