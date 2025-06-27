from django.urls import path
from . import views

app_name = "events"
urlpatterns = [
    # Page for adding new event (creator only)
    path("new_event/", views.new_event, name="new_event"),
    # Page for viewing own created events (creator only)
    path("my_events/", views.my_events, name="my_events"),
    # Detail page for a single event
    path("event_details/<int:event_id>/", views.event_details, name="event_details"),
    # Page for editing created event (creators only)
    path("edit_event/<int:event_id>", views.edit_event, name="edit_event"),
    # Page for export event registrations in CSV
    path(
        "event/<int:event_id>/export_csv",
        views.export_registrations_csv,
        name="export_csv",
    ),
    # Page for confirmation cancel own created event (creator)
    path(
        "events/<int:event_id>/cancel_event/",
        views.cancel_event,
        name="cancel_event",
    ),
    # Page for viewing all events (visitor only)
    path("browse_events/", views.browse_events, name="browse_events"),
    # Page for register on event (visitor only)
    path(
        "events/<int:event_id>/register/",
        views.register_for_event,
        name="register_for_event",
    ),
    # Page for view own registered events (visitor only)
    path("my_registrations/", views.my_registrations, name="my_registrations"),
    # Page for confirmation cancel registration on event (visitor only)
    path(
        "events/<int:event_id>/cancel_registration/",
        views.cancel_registration,
        name="cancel_registration",
    ),
]
