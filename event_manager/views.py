from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.events.models import Event


def index(request):
    """Welcome page."""
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "index.html")


@login_required
def home(request):
    """Home page shows events only for logged-in users"""
    events = Event.objects.order_by("updated_at")
    return render(request, "home.html", {"events": events})


def error_404(request, exception):
    return render(request, "404.html", status=404)
