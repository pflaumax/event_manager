from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserSignupForm(UserCreationForm):
    """
    Custom user registration form with role selection.
    This form extends Django's built-in UserCreationForm to include
    role selection functionality, allowing users to choose between
    different user types during registration.

    Attributes:
        role: ChoiceField for selecting user role (Creator or Visitor).
        Creator can create events, Visitor can register for events
    """

    role: forms.ChoiceField = forms.ChoiceField(
        choices=CustomUser.ROLE_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select your role: Creator can create events, Visitor can register for events.",
    )

    class Meta:
        """Meta configuration for the CustomUserSignupForm."""

        model: type[CustomUser] = CustomUser
        fields: tuple[str, ...] = (
            "email",
            "username",
            "role",
            "password1",
            "password2",
        )
        widgets: dict[str, forms.Widget] = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your username",
                }
            ),
        }
