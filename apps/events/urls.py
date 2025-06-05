from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "events"
urlpatterns = [
    # Page for adding new event (creator only)
    path("new_event/", views.new_event, name="new_event"),
    # Page for viewing events (creator only)
    path("my_events/", views.my_events, name="my_events"),
    # Detail page for a single event
    path("my_events/<int:event_id>/", views.event_details, name="event_details"),
    # Page for viewing all events (visitor only)
    path("browse_events/", views.browse_events, name="browse_events"),
]
