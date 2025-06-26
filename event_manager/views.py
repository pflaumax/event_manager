from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.events.models import Event


def index(request: HttpRequest) -> HttpResponse:
    """
    Render the welcome page for unauthenticated users.
    If the user is already authenticated, redirect them to the home page.
    Otherwise, renders the index template for new visitors.
    Args:
        request: The HTTP request object containing user and session information.
    Returns:
        HttpResponse: Either a redirect to home page for authenticated users
        or rendered index.html template for unauthenticated users.
    """
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "index.html")


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """
    Render the home page with an events list for authenticated users only.
    Displays all events ordered by their last update time (oldest first).
    Requires user authentication via the @login_required decorator.
    Args:
        request: The HTTP request object from an authenticated user.
    Returns:
        HttpResponse: Rendered home.html template with events context.
    """
    events = Event.objects.order_by("updated_at")
    return render(request, "home.html", {"events": events})


def error_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    Handle 404 Didn't Find errors with custom error page.
    This view is called when Django encounters a 404 error and
    DEBUG is False in settings. Renders a custom 404 error page
    instead of the default Django 404 page.
    Args:
        request: The HTTP request object that caused the 404 error.
        exception: The exception that was raised (usually Http404).
    Returns:
        HttpResponse: Rendered 404.html template with 404 status codes.
    Note:
        This view requires DEBUG = False in settings.py to be triggered.
        For development with DEBUG = True, Django shows its default 404 page.
    """
    return render(request, "404.html", status=404)
