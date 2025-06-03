from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.events.models import Event
from apps.users.models import CustomUser


def index(request):
    """Start page."""
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "index.html")


def home(request):
    """Home page shows events only for logged-in users"""
    events = Event.objects.filter(status="published")
    return render(request, "home.html", {"events": events})
