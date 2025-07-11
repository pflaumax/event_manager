from rest_framework import serializers
from typing import Dict, Any
from .models import CustomUser
from apps.events.models import EventRegistration


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "role"]

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """Create new user with hashed password."""
        user = CustomUser(
            email=validated_data["email"],
            role=validated_data.get("role", "visitor"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (no password)"""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class MyRegistrationsSerializer(serializers.ModelSerializer):
    """Simplified serializer for user's registrations."""

    event_title = serializers.ReadOnlyField(source="event.title")
    event_date = serializers.ReadOnlyField(source="event.date")
    event_location = serializers.ReadOnlyField(source="event.location")

    class Meta:
        model = EventRegistration
        fields = ["id", "event_title", "event_date", "event_location", "registered_at"]
