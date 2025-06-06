from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Event, EventRegistration
from .forms import EventForm


@login_required
def new_event(request):
    """Create a new event - only creators allowed."""
    # Check if user can create events
    if not request.user.can_create_events():
        messages.error(request, "You are not allowed to create events.")
        return redirect("home")

    if request.method == "POST":
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            # Save event and set creator
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "New event created successfully!")
            return redirect("events:my_events")
    else:
        # Show empty form for GET request
        form = EventForm()

    return render(request, "events/new_event.html", {"form": form})


@login_required
def my_events(request):
    """Show events created by current creator."""
    if not request.user.is_creator:
        raise Http404("You are not allowed to view this events.")

    # Get user's events
    events = Event.objects.filter(created_by=request.user)
    return render(request, "events/my_events.html", {"events": events})


@login_required
def event_details(request, event_id):
    """Show single event details."""
    event = get_object_or_404(Event, id=event_id)

    # Creators can only see their own events
    if request.user.is_creator and event.created_by != request.user:
        raise Http404("You are not allowed to view this event details.")

    # Check if visitor can register for event
    can_register, message = event.can_register(request.user)
    registration = event.registrations.filter(user=request.user).first()

    context = {
        "event": event,
        "can_register": can_register,
        "register_message": message,
        "registration": registration,
    }
    return render(request, "events/event_details.html", context)


@login_required
def cancel_event(request, event_id):
    """Display confirmation page for canceling event."""
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        try:
            event.cancel_event(request.user)
            messages.success(request, "Event cancelled successfully.")
            return redirect("events:my_events")
        except (PermissionError, ValueError) as e:
            messages.error(request, str(e))
            return redirect("events:event_details", event_id=event_id)

    return render(request, "events/cancel_event.html", {"event": event})


@login_required
def browse_events(request):
    """Browse all events with optional status filter."""
    status = request.GET.get("status", "published")
    events = Event.objects.filter(status=status).order_by("date", "start_time")

    context = {"events": events, "status": status}
    return render(request, "events/browse_events.html", context)


@login_required
def register_for_event(request, event_id):
    """Register visitor for an event with confirmation."""
    event = get_object_or_404(Event, id=event_id)

    # Check if registration is allowed
    can_register, message = event.can_register(request.user)
    if not can_register:
        messages.error(request, message)
        return redirect("events:event_details", event_id=event_id)

    if request.method == "POST":
        # Create registration
        EventRegistration.objects.create(
            event=event, user=request.user, status="registered"
        )
        messages.success(request, "Successfully registered!")
        return redirect("events:event_details", event_id=event_id)

    # Show confirmation page
    return render(request, "events/register_confirm.html", {"event": event})


@login_required
def my_registrations(request):
    """Show visitor's event registrations."""
    registrations = (
        EventRegistration.objects.filter(user=request.user, status="registered")
        .select_related("event")
        .order_by("event__date")
    )

    return render(
        request, "events/my_registrations.html", {"registrations": registrations}
    )


@login_required
def cancel_registration(request, event_id):
    """Display confirmation page for canceling registration"""
    event = get_object_or_404(Event, id=event_id)
    registration = event.registrations.filter(user=request.user).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect("events:event_details", event_id=event_id)

    if request.method == "POST":
        registration.cancel_registration()
        messages.success(request, "Registration cancelled successfully.")
        return redirect("events:my_registrations")

    # Show confirmation page
    return render(request, "events/cancel_registration.html", {"event": event})
