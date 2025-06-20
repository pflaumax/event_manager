import csv
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, EventRegistration
from .forms import EventForm
from apps.users.views import (
    send_event_registration_email,
    send_event_cancellation_emails,
)


@login_required
def new_event(request):
    """Create a new event - only creators allowed."""
    # Check if user can create events
    if not request.user.can_create_events():
        messages.error(request, "You are not allowed to create events.")
        return redirect("home")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, user=request.user)
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
def edit_event(request, event_id):
    """Edit event details by current creator."""
    event = get_object_or_404(Event, id=event_id)

    if not request.user.is_creator and event.created_by != request.user:
        raise Http404("You are not allowed to edit this event.")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            # Save edited event
            event.save()
            messages.success(request, "Event edited successfully.")
            return redirect("events:my_events")
    else:
        # Show empty form for GET request
        form = EventForm(instance=event, user=request.user)
    context = {
        "form": form,
        "event": event,
    }
    return render(request, "events/edit_event.html", context)


@login_required
def export_registrations_csv(request, event_id):
    """Export all visitors registrations data for one event in CSV format."""
    event = get_object_or_404(Event, id=event_id)

    if not request.user.is_creator or event.created_by != request.user:
        raise Http404("You are not allowed to export this event.")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="event_{event_id}_registrations.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Username", "Email", "Registered at"])

    registrations = event.registrations.select_related("user").all()
    for registration in registrations:
        writer.writerow(
            [
                registration.user.username,
                registration.user.email,
                registration.registered_at.strftime("%H:%M %d-%m-%Y"),
            ]
        )

    return response


@login_required
def cancel_event(request, event_id):
    """Display confirmation page for canceling event."""
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        try:
            # Freeze QuerySet to avoid changes after event cancellation
            registrations = list(event.registrations.filter(status="registered"))
            print("All registrations before cancelling:", registrations)
            print("Count:", len(registrations))
            # Cancel the event
            event.cancel_event(request.user)

            # Send cancellation emails to all registered users
            if registrations:
                print("Sending cancellation emails...")  # Debug
                send_event_cancellation_emails(request, event, registrations)

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
    search_query = request.GET.get("q", "")
    event_date = request.GET.get("date", "")
    events = Event.objects.filter(status=status).order_by("date", "start_time")

    if search_query:
        events = events.filter(Q(title__icontains=search_query))
    if event_date:
        events = events.filter(date=event_date)

    context = {
        "events": events,
        "status": status,
        "search_query": search_query,
        "event_date": event_date,
    }
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
        registration = EventRegistration.objects.create(
            event=event, user=request.user, status="registered"
        )

        # Send confirmation email to the user
        try:
            send_event_registration_email(request, registration)
        except Exception as e:
            # If email fails, log it but don't break the registration
            print(f"Failed to send registration email: {e}")
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
    registration = event.registrations.filter(
        user=request.user, status="registered"
    ).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect("events:event_details", event_id=event_id)

    if request.method == "POST":
        try:
            registration.cancel_registration()
            messages.success(request, "Registration cancelled successfully.")
            return redirect("events:my_registrations")
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("events:my_registrations")

    # GET: check if can show confirmation page
    if not registration.can_cancel():
        messages.error(request, f"Cannot cancel registration.")
        return redirect("events:my_registrations")

    return render(request, "events/cancel_registration.html", {"event": event})
