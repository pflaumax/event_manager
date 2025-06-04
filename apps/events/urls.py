from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "events"
urlpatterns = [
    # Detail page for a single event
    path("event/<int:event_id>/", views.event_details, name="event_details"),
]
