from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count
from typing import Any
from .permissions import IsCreatorOrReadOnly, IsEventCreator
from .models import Event, EventRegistration
from .serializers import (
    EventListSerializer,
    EventSerializer,
    EventRegistrationSerializer,
    MyRegistrationsSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for event management with additional custom actions."""

    queryset = Event.objects.all()
    permission_classes = [
        IsAuthenticated,
        IsAuthenticatedOrReadOnly,
        IsCreatorOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["date", "location", "status"]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["date", "created_at", "title"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return EventListSerializer
        return EventSerializer

    def get_queryset(self):
        """Filter queryset based on action and user role."""
        queryset = Event.objects.all()

        # Add registration count annotation
        return Event.objects.annotate(registered_count=Count("registrations"))

    def perform_create(self, serializer: EventSerializer) -> None:
        """Save event with current user as creator."""
        # Only Event Creators can create events
        if self.request.user.role != "creator":
            raise PermissionError("Only Event Creators can create events")
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        """Get events created by current user."""
        if request.user.role != "creator":
            return Response(
                {"detail": "Only Event Creators can view their events."},
                status=status.HTTP_403_FORBIDDEN,
            )

        events = self.get_queryset().filter(created_by=request.user)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming events."""
        upcoming_events = self.get_queryset().filter(
            date__gte=timezone.now().date(), status="published"
        )
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel an event (creator only)."""
        event = self.get_object()

        if event.created_by != request.user:
            return Response(
                {"detail": "Only the event creator can cancel this event."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if event.status == "cancelled":
            return Response(
                {"detail": "Event is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.cancel_event()
        return Response(
            {"detail": "Event cancelled successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def registrations(self, request, pk=None):
        """Get registrations for an event (creator only)."""
        event = self.get_object()

        if event.created_by != request.user:
            return Response(
                {"detail": "Only the event creator can view registrations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        registrations = event.registrations.all()
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get event statistics for current user."""
        if request.user.role != "creator":
            return Response(
                {"detail": "Only Event Creators can view statistics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_events = Event.objects.filter(created_by=request.user)
        stats = {
            "total_events": user_events.count(),
            "active_events": user_events.filter(status="published").count(),
            "completed_events": user_events.filter(status="completed").count(),
            "cancelled_events": user_events.filter(status="cancelled").count(),
            "total_registrations": EventRegistration.objects.filter(
                event__created_by=request.user
            ).count(),
        }
        return Response(stats)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing event registrations."""

    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only current user's registrations."""
        return EventRegistration.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create registration with validation."""
        user = self.request.user

        # Only visitors can register for events
        if user.role != "visitor":
            raise PermissionError("Only Visitors can register for events")

        event = serializer.validated_data["event"]

        # Check if event is active
        if event.status != "published":
            raise PermissionError("Cannot register for inactive events")

        # Check if event date has passed
        if event.date < timezone.now().date():
            raise PermissionError("Cannot register for past events")

        serializer.save(user=user)

    def destroy(self, request, *args, **kwargs):
        """Cancel registration."""
        registration = self.get_object()

        # Check if registration can be cancelled
        if not registration.can_cancel():
            return Response(
                {"detail": "Registration cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration.status = "cancelled"
        registration.save()

        return Response(
            {"detail": "Registration cancelled successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get user's upcoming event registrations."""
        upcoming_registrations = self.get_queryset().filter(
            event__date__gte=timezone.now().date(), status="registered"
        )
        serializer = MyRegistrationsSerializer(upcoming_registrations, many=True)
        return Response(serializer.data)
