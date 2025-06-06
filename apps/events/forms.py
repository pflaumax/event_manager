from django.core.exceptions import ValidationError
from django import forms
from .models import Event
from .models import EventRegistration


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            "title",
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
        self.user = kwargs.pop("user", None)  # get user from view
        super().__init__(*args, **kwargs)
