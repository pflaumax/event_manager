from django.core.exceptions import ValidationError
from django import forms
from .models import Event


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
            "date": forms.DateInput(attrs={"placeholder": "YYYY-MM-DD"}),
            "start_time": forms.TimeInput(attrs={"placeholder": "HH:MM"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # get user from view
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.user.is_creator:
            raise ValidationError("Only users with role 'creator' can create events.")
        return cleaned_data
