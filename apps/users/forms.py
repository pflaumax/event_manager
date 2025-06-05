from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserSignupForm(UserCreationForm):
    """Custom user registration form with role selection."""

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select your role: Creator can create events, Visitor can register for events.",
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username", "role", "password1", "password2")
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email address",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your username or pseudonym",
                }
            ),
        }
