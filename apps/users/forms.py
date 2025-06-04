from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm


class CustomUserSignupForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_TYPE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ("email", "username", "role", "password1", "password2")
