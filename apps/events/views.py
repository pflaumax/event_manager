from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Event
from .forms import EventForm
from .models import EventRegistration


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

    # Restrict creators to their own events only
    if request.user.is_creator and event.created_by != request.user:
        raise Http404("You are not allowed to view this event.")

    can_register, register_message = event.can_register(request.user)

    # Check if user is visitor and if event status is published
    registration = None
    if request.user.is_authenticated:
        registration = event.registrations.filter(user=request.user).first()

    context = {
        "event": event,
        "can_register": can_register,
        "register_message": register_message,
        "registration": registration,
    }
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


@login_required
@require_POST
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = event.registrations.filter(user=request.user).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect("events:event_details", event_id=event.id)

    try:
        registration.cancel_registration()
        messages.success(request, "Your registration was cancelled.")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect("events:event_details", event_id=event.id)


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    can_register, message = event.can_register(request.user)
    if not can_register:
        messages.error(request, message)
        return redirect("events:event_details", event_id=event.id)

    if request.method == "POST":
        registration = EventRegistration.objects.create(
            event=event, user=request.user, status="registered"
        )
        messages.success(request, "Successfully registered!")
        return redirect("events:event_details", event_id=event.id)

    return render(request, "events/register_confirm.html", {"event": event})


@login_required
def my_registrations(request):
    # get all registrations for current visitor
    registrations = (
        EventRegistration.objects.filter(user=request.user, status="registered")
        .select_related("event")
        .order_by("event__date")
    )

    context = {
        "registrations": registrations,
    }
    return render(request, "events/my_registrations.html", context)
