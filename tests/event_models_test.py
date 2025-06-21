from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from datetime import datetime, timedelta
from django.utils import timezone
from freezegun import freeze_time
from tests.factories import (
    CreatorFactory,
    VisitorFactory,
    EventFactory,
    PastEventFactory,
)
from apps.events.models import Event, EventRegistration


class EventModelTest(TestCase):
    """Test cases for Event model."""

    def setUp(self):
        self.creator = CreatorFactory()
        self.visitor = VisitorFactory()

    def test_create_event_with_valid_data(self):
        """Test creating event with valid data."""
        event = EventFactory(created_by=self.creator)
        self.assertEqual(event.status, "published")
        self.assertEqual(event.created_by, self.creator)

    def test_create_event_with_empty_title(self):
        """Test that creating event with empty title raises ValidationError."""
        with self.assertRaises(ValidationError):
            event = Event(
                title="",
                description="Test description",
                location="Test Location",
                date=datetime.now() + timedelta(days=7),
                start_time=timezone.now() + timedelta(days=1),
                created_by=self.creator,
            )
            event.full_clean()

    def test_create_event_with_empty_location(self):
        """Test that creating event with empty location raises ValidationError."""
        with self.assertRaises(ValidationError):
            event = Event(
                title="Test Event",
                description="Test description",
                location="",
                date=datetime.now() + timedelta(days=7),
                start_time=timezone.now() + timedelta(days=1),
                created_by=self.creator,
            )
            event.full_clean()

    def test_visitor_cannot_create_event(self):
        """Test that visitor cannot create event."""
        with self.assertRaises(PermissionDenied):
            event = Event(
                title="Test Event",
                description="Test description",
                location="Test Location",
                date=datetime.now() + timedelta(days=7),
                start_time=timezone.now() + timedelta(days=1),
                created_by=self.visitor,
            )
            event.save()

    def test_past_event_auto_marked_completed(self):
        """Test that past event is automatically marked as completed."""
        past_date = datetime.now() - timedelta(days=1)
        event = Event(
            title="Past Event",
            description="Past event description",
            location="Test Location",
            date=past_date,
            start_time=timezone.now() + timedelta(days=1),
            created_by=self.creator,
            status="published",
        )
        event.save()
        self.assertEqual(event.status, "completed")

    def test_cancel_published_event(self):
        """Test canceling a published event."""
        event = EventFactory(created_by=self.creator, status="published")
        event.cancel_event(user=self.creator)
        self.assertEqual(event.status, "cancelled")

    def test_cancel_already_cancelled_event(self):
        """Test that canceling already cancelled event raises ValueError."""
        event = EventFactory(created_by=self.creator, status="cancelled")
        with self.assertRaises(ValueError):
            event.cancel_event(user=self.creator)

    def test_visitor_cannot_cancel_event(self):
        """Test that visitor cannot cancel event."""
        event = EventFactory(created_by=self.creator)
        with self.assertRaises(PermissionError):
            # Simulate visitor trying to cancel
            event.cancel_event(user=self.visitor)

    def test_event_str_representation(self):
        """Test event string representation."""
        event = EventFactory(title="Test Event")
        self.assertEqual(str(event), "Test Event - 2025-06-28 (published)")
