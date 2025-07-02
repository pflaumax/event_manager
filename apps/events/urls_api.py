from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import EventViewSet, EventRegistrationViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event_details")
router.register(r"registrations", EventRegistrationViewSet, basename="registrations")

urlpatterns = [
    path("api/", include(router.urls)),
]
