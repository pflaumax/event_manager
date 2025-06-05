from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm


@login_required
def new_event(request):
    """Add new event (by creator only)"""
    # Block if not creator
    if not request.user.is_creator:
        return redirect("home")  # or render some 'permission denied' page

    if request.method == "POST":
        # Data submitted; create a blank form
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect("home")
    else:
        form = EventForm()

    # Display a blank or invalid form
    context = {"form": form}
    return render(request, "events/new_event.html", context)


@login_required
def my_events(request):
    """View events created by the logged-in creator"""
    if not request.user.is_creator:
        return render(request, "events/not_creator.html")

    events = Event.objects.filter(created_by=request.user)

    context = {"events": events}
    return render(request, "events/my_events.html", context)


@login_required
def event_details(request, event_id):
    """Show a single event and all its information"""
    event = get_object_or_404(Event, id=event_id)

    if request.user.is_creator and event.created_by != request.user:
        raise Http404("You are not allowed to view this event.")

    context = {"event": event}
    return render(request, "events/event_details.html", context)


@login_required
def browse_events(request):
    status = request.GET.get("status", "published")
    events = Event.objects.filter(status=status).order_by("date", "start_time")
    return render(
        request,
        "events/browse_events.html",
        {
            "events": events,
            "status": status,
        },
    )
