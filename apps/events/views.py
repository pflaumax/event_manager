from django.shortcuts import render, get_object_or_404
from apps.events.models import Event


def event_details(request, event_id):
    """Show a single event and all its information"""
    event = get_object_or_404(Event, id=event_id)
    context = {"event": event}
    return render(request, "events/event_details.html", context)
