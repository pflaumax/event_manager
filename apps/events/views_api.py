from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from typing import Any
from .permissions import IsCreatorOrReadOnly
from .models import Event, EventRegistration
from .serializers import (
    EventListSerializer,
    EventSerializer,
    EventRegistrationSerializer,
    MyRegistrationsSerializer,
)


class EventListViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating events."""

    queryset = Event.objects.all()
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["date", "location", "status"]
    search_fields = ["title", "description"]
    ordering_fields = ["date", "created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer: EventListSerializer) -> None:
        """Save event with current user as creator."""
        serializer.save(created_by=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for detailed event operations."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly]

    def perform_create(self, serializer: EventSerializer) -> None:
        """Save event with current user as creator."""
        serializer.save(created_by=self.request.user)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing event registrations."""

    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only current user's registrations."""
        return EventRegistration.objects.filter(user=self.request.user)
