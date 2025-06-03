from django.shortcuts import render, redirect
from .models import CustomUser
from .forms import UserForm


def signup(request):
    """User registration page."""
    return render(request, "users/signup.html")


def login(request):
    """User registration page."""
    return render(request, "users/login.html")
