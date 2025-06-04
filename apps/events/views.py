from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm


@login_required
def event_details(request, event_id):
    """Show a single event and all its information"""
    event = get_object_or_404(Event, id=event_id)
    context = {"event": event}
    return render(request, "events/event_details.html", context)


@login_required
def new_event(request):
    """Add new event (by creator)"""
    if request.method == "POST":
        # Data submitted; create a blank form
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            form.save()
            return redirect("home")
    else:
        form = EventForm()

    # Display a blank or invalid form
    context = {"form": form}
    return render(request, "events/new_event.html", context)
