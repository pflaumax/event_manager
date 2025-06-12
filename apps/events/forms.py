from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    """A form for creating or editing events."""

    class Meta:
        model = Event
        fields = [
            "title",
            "image",
            "description",
            "location",
            "date",
            "start_time",
        ]

        widgets = {
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

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and optionally stores the user
        passed in from the view for use in validation.
        """

        self.user = kwargs.pop("user", None)  # Get user from view
        super().__init__(*args, **kwargs)
