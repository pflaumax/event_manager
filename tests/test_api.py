from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.events.models import Event, EventRegistration
from datetime import date, timedelta

User = get_user_model()


class EventAPITest(APITestCase):
    """Test cases for Event API endpoints."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            date=date.today() + timedelta(days=1),
            location="Test Location",
            created_by=self.user,
        )

    def test_get_events_list(self) -> None:
        """Test getting events list without authentication."""
        response = self.client.get("/api/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event_authenticated(self) -> None:
        """Test creating event with authentication."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Event",
            "description": "New Description",
            "date": "2025-08-01",
            "location": "New Location",
        }
        response = self.client.post("/api/events/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_event_unauthenticated(self) -> None:
        """Test creating event without authentication."""
        data = {
            "title": "New Event",
            "description": "New Description",
            "date": "2025-08-01",
            "location": "New Location",
        }
        response = self.client.post("/api/events/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_for_event(self) -> None:
        """Test registering for an event."""
        self.client.force_authenticate(user=self.user)
        data = {"event": self.event.id}
        response = self.client.post("/api/registrations/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_my_registrations(self) -> None:
        """Test getting user's registrations."""
        self.client.force_authenticate(user=self.user)
        EventRegistration.objects.create(user=self.user, event=self.event)
        response = self.client.get("/api/registrations/my_registrations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class UserAPITest(APITestCase):
    """Test cases for User API endpoints."""

    def test_user_registration(self) -> None:
        """Test user registration endpoint."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "role": "visitor",
        }
        response = self.client.post("/api/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)

    def test_user_login(self) -> None:
        """Test user login endpoint."""
        user = User.objects.create_user(
            username="loginuser", email="login@example.com", password="loginpass123"
        )
        data = {"username": "loginuser", "password": "loginpass123"}
        response = self.client.post("/api/users/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
