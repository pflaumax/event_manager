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


"""
Custom error handlers for HTTP status codes.

This module provides user-friendly error pages for common HTTP error responses.
Each handler function renders a corresponding HTML template with an appropriate
HTTP status code.

Handlers:
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 500 Internal Server Error
- 503 Service Unavailable
"""


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)


def handler403(request, exception):
    return render(request, "errors/403.html", status=403)


def handler401(request, exception):
    return render(request, "errors/401.html", status=401)


def handler503(request, exception):
    return render(request, "errors/503.html", status=503)
