from rest_framework import serializers
from datetime import date as dt_date
from typing import Dict, Any
from .models import Event, EventRegistration


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for event list view with minimal fields."""

    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "location",
            "date",
            "start_time",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]


class EventSerializer(serializers.ModelSerializer):
    """Detailed serializer for event with additional fields."""

    created_by = serializers.ReadOnlyField(source="created_by.username")
    registered_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "location",
            "date",
            "start_time",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_registered_count(self, obj: Event) -> int:
        """Get count of users registered for this event."""
        return obj.registrations.count()  # type: ignore

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event data."""
        event_date = data.get("date")
        if event_date and event_date < dt_date.today():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return data


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for event registrations."""

    user = serializers.ReadOnlyField(source="user.username")
    event_title = serializers.ReadOnlyField(source="event.title")
    registered_at = serializers.ReadOnlyField()

    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "user",
            "event",
            "status",
            "registered_at",
            "updated_at",
        ]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate registration data to prevent duplicates."""
        user = self.context["request"].user
        event = data.get("event")

        if EventRegistration.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )
        return data

    def create(self, validated_data: Dict[str, Any]) -> EventRegistration:
        """Create registration with current user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class MyRegistrationsSerializer(serializers.ModelSerializer):
    """Simplified serializer for user's own registrations."""

    event_title = serializers.ReadOnlyField(source="event.title")
    event_date = serializers.ReadOnlyField(source="event.date")
    event_location = serializers.ReadOnlyField(source="event.location")

    class Meta:
        model = EventRegistration
        fields = ["id", "event_title", "event_date", "event_location", "registered_at"]
