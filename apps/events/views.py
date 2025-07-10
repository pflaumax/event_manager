import csv
from typing import Union, List, Optional, TYPE_CHECKING, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from .models import Event, EventRegistration
from .forms import EventForm
from apps.users.views import (
    send_event_registration_email,
    send_event_cancellation_emails,
)

if TYPE_CHECKING:
    from apps.users.models import CustomUser


@login_required
def new_event(request: HttpRequest) -> HttpResponse:
    """
    Create a new event - only creators allowed.
    Args:
        request: The HTTP request object.
    Returns:
        HttpResponse: Rendered template for event creation or redirect after successful creation.
    Raises:
        None: Redirects with an error message if user cannot create events.
    """
    # Check if user can create events
    user = cast("CustomUser", request.user)
    if not hasattr(user, "can_create_events") or not user.can_create_events():
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
        form = EventForm(user=request.user)

    return render(request, "events/new_event.html", {"form": form})


@login_required
def my_events(request: HttpRequest) -> HttpResponse:
    """
    Show events created by the current creator.
    Args:
        request: The HTTP request object.
    Returns:
        HttpResponse: Rendered template with user's created events.
    Raises:
        Http404: If user is not a creator.
    """
    user = cast("CustomUser", request.user)
    if not hasattr(user, "is_creator") or not user.is_creator:
        raise Http404("You are not allowed to view these events.")

    # Get user's events
    events: QuerySet[Event] = Event.objects.filter(created_by=request.user)
    return render(request, "events/my_events.html", {"events": events})


@login_required
def event_details(
    request: HttpRequest, event_id: int
) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Show single event details.

    Args:
        request: The HTTP request object.
        event_id: The ID of the event to display.

    Returns:
        HttpResponse: Rendered template with event details.

    Raises:
        Http404: If an event doesn't exist or user lacks permission to view it.
    """
    event: Event = get_object_or_404(Event, id=event_id)

    # Creators can only see their own events
    user = cast("CustomUser", request.user)
    if (
        hasattr(user, "is_creator")
        and user.is_creator
        and event.created_by != request.user
    ):
        raise Http404("You are not allowed to view this event details.")

    # Check if a visitor can register for event
    can_register: bool
    message: str
    can_register, message = event.can_register(request.user)

    registration: Optional[EventRegistration] = None
    if hasattr(event, "registrations"):
        registration = event.registrations.filter(user=request.user, status="registered").first()  # type: ignore

    is_registered = registration is not None

    context = {
        "event": event,
        "can_register": can_register,
        "register_message": message,
        "registration": registration,
        "is_registered": is_registered,
    }
    return render(request, "events/event_details.html", context)


@login_required
def edit_event(
    request: HttpRequest, event_id: int
) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Edit event details by current creator.
    Args:
        request: The HTTP request object.
        event_id: The ID of the event to edit.
    Returns:
        HttpResponse: Rendered template for event editing or redirect after successful edit.
    Raises:
        Http404: If an event doesn't exist or user lacks permission to edit it.
    """
    event: Event = get_object_or_404(Event, id=event_id)

    user = cast("CustomUser", request.user)
    if (
        not hasattr(user, "is_creator")
        or not user.is_creator
        or event.created_by != request.user
    ):
        raise Http404("You are not allowed to edit this event.")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            # Save edited event
            form.save()
            messages.success(request, "Event edited successfully.")
            return redirect("events:my_events")
    else:
        # Show a form with existing data for GET request
        form = EventForm(instance=event, user=request.user)

    context = {
        "form": form,
        "event": event,
    }
    return render(request, "events/edit_event.html", context)


@login_required
def export_registrations_csv(
    request: HttpRequest, event_id: int
) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Export all visitor registrations data for one event in CSV format.
    Args:
        request: The HTTP request object.
        event_id: The ID of the event to export registrations for.
    Returns:
        HttpResponse: CSV file download response.
    Raises:
        Http404: If event doesn't exist or user lacks permission to export.
    """
    event: Event = get_object_or_404(Event, id=event_id)

    user = cast("CustomUser", request.user)
    if (
        not hasattr(user, "is_creator")
        or not user.is_creator
        or event.created_by != request.user
    ):
        raise Http404("You are not allowed to export this event.")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="event_{event_id}_registrations.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Username", "Email", "Registered at"])

    registrations: QuerySet[EventRegistration]
    if hasattr(event, "registrations"):
        registrations = event.registrations.select_related("user").all()  # type: ignore
    else:
        registrations = EventRegistration.objects.none()

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
def cancel_event(
    request: HttpRequest, event_id: int
) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Display confirmation page for cancelling event.
    Args:
        request: The HTTP request object.
        event_id: The ID of the event to cancel.
    Returns:
        HttpResponse: Rendered confirmation template or redirect after cancellation.
    Raises:
        Http404: If event doesn't exist.
    """
    event: Event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        try:
            # Freeze QuerySet to avoid changes after event cancellation
            registrations: List[EventRegistration] = []
            if hasattr(event, "registrations"):
                registrations = list(event.registrations.filter(status="registered"))  # type: ignore

            print(f"All registrations before cancelling: {registrations}")
            print(f"Count: {len(registrations)}")

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
def browse_events(request: HttpRequest) -> HttpResponse:
    """
    Browse all events with optional status filter.
    Args:
        request: The HTTP request object.
    Returns:
        HttpResponse: Rendered template with a filtered events list.
    """
    status: str = request.GET.get("status", "published")
    search_query: str = request.GET.get("q", "")
    event_date: str = request.GET.get("date", "")

    events: QuerySet[Event] = Event.objects.filter(status=status).order_by(
        "date", "start_time"
    )

    if search_query:
        events = events.filter(Q(title__icontains=search_query))
    if event_date:
        events = events.filter(date=event_date)

    # Annotate events with can_register
    events_with_flags = []
    for event in events:
        can_register, _ = event.can_register(request.user)
        events_with_flags.append((event, can_register))

    context = {
        "events_with_flags": events_with_flags,
        "events": events,
        "status": status,
        "search_query": search_query,
        "event_date": event_date,
    }
    return render(request, "events/browse_events.html", context)


@login_required
def register_for_event(
    request: HttpRequest, event_id: int
) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Register a visitor for an event with confirmation.
    Args:
        request: The HTTP request object.
        event_id: The ID of the event to register for.
    Returns:
        HttpResponse: Rendered confirmation template or redirect after registration.
    Raises:
        Http404: If event doesn't exist.
    """
    event: Event = get_object_or_404(Event, id=event_id)

    # Check if registration is allowed
    can_register: bool
    message: str
    can_register, message = event.can_register(request.user)
    if not can_register:
        messages.error(request, message)
        return redirect("events:event_details", event_id=event_id)

    if request.method == "POST":
        # Check for existing registration
        registration: Optional[EventRegistration] = EventRegistration.objects.filter(
            user=request.user,
            event=event,
        ).first()

        if registration:
            if registration.status == "cancelled":
                # Re-activate cancelled registration
                registration.status = "registered"
                registration.save()
                messages.success(request, "You have re-registered for this event.")
            else:
                messages.warning(request, "You are already registered for this event.")
                return redirect("events:event_details", event_id=event_id)
        else:
            # Create new registration
            registration = EventRegistration.objects.create(
                event=event, user=request.user, status="registered"
            )
            messages.success(request, "Successfully registered!")

        # Send confirmation email
        try:
            send_event_registration_email(request, registration)
        except Exception as e:
            print(f"Failed to send registration email: {e}")

        return redirect("events:event_details", event_id=event_id)

    # Show confirmation page
    return render(request, "events/register_confirm.html", {"event": event})


@login_required
def my_registrations(request: HttpRequest) -> HttpResponse:
    """
    Show visitor's event registrations.
    Args:
        request: The HTTP request object.
    Returns:
        HttpResponse: Rendered template with user's registrations.
    """
    registrations: QuerySet[EventRegistration] = (
        EventRegistration.objects.filter(
            user=request.user, status__in=["registered", "cancelled"]
        )
        .select_related("event")
        .order_by("event__date")
    )

    return render(
        request, "events/my_registrations.html", {"registrations": registrations}
    )


@login_required
def cancel_registration(
    request: HttpRequest, event_id: int
) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Display confirmation page for cancelling registration.
    Args:
        request: The HTTP request object.
        event_id: The ID of the event to cancel registration for.
    Returns:
        HttpResponse: Rendered confirmation template or redirect after cancellation.
    Raises:
        Http404: If event doesn't exist.
    """
    event: Event = get_object_or_404(Event, id=event_id)
    registration: Optional[EventRegistration] = None

    if hasattr(event, "registrations"):
        registration = event.registrations.filter(  # type: ignore
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

    # GET: check if it can show confirmation page
    if not registration.can_cancel():
        messages.error(request, "Cannot cancel registration.")
        return redirect("events:my_registrations")

    return render(request, "events/cancel_registration.html", {"event": event})
