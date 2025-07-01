from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import EventViewSet, EventRegistrationViewSet


router = DefaultRouter()
router.register(r"events", EventViewSet)
router.register(r"registrations", EventRegistrationViewSet)

urlpatterns = [
    # Add events API URL
    path("api/", include(router.urls)),
]
