from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import EventListViewSet, EventViewSet, EventRegistrationViewSet

router = DefaultRouter()
router.register(r"events", EventListViewSet, basename="event_list")
router.register(r"event-details", EventViewSet, basename="event_details")
router.register(r"registrations", EventRegistrationViewSet, basename="registrations")

urlpatterns = [
    path("api/", include(router.urls)),
]
