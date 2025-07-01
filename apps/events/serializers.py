from rest_framework import serializers
from datetime import date as dt_date
from .models import Event, EventRegistration


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for event list view"""

    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Event
        fields = [
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
    created_by = serializers.ReadOnlyField(source="created_by.username")
    registered_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
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

    def get_registered_count(self, obj):
        return obj.registrations.count()

    def validate(self, data):
        event_date = data.get("date")
        if event_date and event_date < dt_date.today():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    event_title = serializers.ReadOnlyField(source="event.title")
    registered_at = serializers.ReadOnlyField()

    class Meta:
        model = EventRegistration
        fields = [
            "user",
            "event",
            "status",
            "registered_at",
            "updated_at",
        ]

    def validate(self, data):
        user = self.context["request"].user
        event = data.get("event")

        if EventRegistration.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )
        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
