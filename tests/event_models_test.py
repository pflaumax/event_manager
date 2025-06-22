from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from datetime import timedelta
from django.utils import timezone
from tests.factories import (
    CreatorFactory,
    VisitorFactory,
    EventFactory,
    PastEventFactory,
    RegistrationFactory,
)


class EventModelTest(TestCase):
    """Test cases for Event class model."""

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
            event = EventFactory.build(title="", created_by=self.creator)
            event.full_clean()

    def test_create_event_with_empty_location(self):
        """Test that creating event with empty location raises ValidationError."""
        with self.assertRaises(ValidationError):
            event = EventFactory.build(location="", created_by=self.creator)
            event.full_clean()

    def test_visitor_cannot_create_event(self):
        """Test that visitor cannot create event."""
        with self.assertRaises(PermissionDenied):
            event = EventFactory.build(created_by=self.visitor)
            event.save()

    def test_past_event_auto_marked_completed(self):
        """Test that past event is automatically marked as completed."""
        event = EventFactory.build(
            date=timezone.now().date() - timedelta(days=1),
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
            event.cancel_event(user=self.visitor)

    def test_event_str_representation(self):
        """Test event string representation."""
        event = EventFactory(title="Test Event")
        self.assertEqual(str(event), "Test Event - 2025-06-29 (published)")


class RegistrationModelTest(TestCase):
    """Test cases for EventRegistration class model."""

    def setUp(self):
        self.creator = CreatorFactory()
        self.visitor = VisitorFactory()
        self.event = EventFactory(created_by=self.creator)

    def test_visitor_register_for_future_event(self):
        """Test visitor registration for future event."""
        registration = RegistrationFactory(user=self.visitor, event=self.event)
        self.assertEqual(registration.status, "registered")
        self.assertEqual(registration.user, self.visitor)
        self.assertEqual(registration.event, self.event)

    def test_visitor_cannot_register_twice(self):
        """Test that visitor cannot register twice for same event."""
        RegistrationFactory(user=self.visitor, event=self.event)
        with self.assertRaises(ValidationError):
            registration = RegistrationFactory.build(
                user=self.visitor, event=self.event
            )
            registration.full_clean()

    def test_creator_cannot_register_for_event(self):
        """Test that creator cannot register for any event."""
        with self.assertRaises(ValidationError):
            registration = RegistrationFactory.build(
                user=self.creator, event=self.event
            )
            registration.full_clean()

    def test_cannot_register_for_cancelled_event(self):
        """Test that user cannot register for cancelled event."""
        cancelled_event = EventFactory(created_by=self.creator, status="cancelled")
        with self.assertRaises(ValidationError):
            registration = RegistrationFactory.build(
                user=self.visitor, event=cancelled_event
            )
            registration.full_clean()

    def test_cannot_register_for_completed_event(self):
        """Test that user cannot register for completed event."""
        completed_event = PastEventFactory(created_by=self.creator)
        with self.assertRaises(ValidationError):
            registration = RegistrationFactory.build(
                user=self.visitor, event=completed_event
            )
            registration.full_clean()

    def test_cancel_registration(self):
        """Test canceling registration."""
        registration = RegistrationFactory(user=self.visitor, event=self.event)
        registration.cancel_registration()
        self.assertEqual(registration.status, "cancelled")

    def test_cannot_cancel_registration_after_event(self):
        """Test that registration cannot be cancelled after event date."""
        future_event = EventFactory(
            date=timezone.now().date() + timedelta(days=1), created_by=self.creator
        )
        registration = RegistrationFactory(
            user=self.visitor, event=future_event, status="registered"
        )
        # Modify event to be in the past
        future_event.date = timezone.now().date() - timedelta(days=1)
        future_event.save()

        with self.assertRaisesMessage(ValueError, "Cannot cancel this registration."):
            registration.cancel_registration()

    def test_cannot_cancel_registration_twice(self):
        """Test that registration cannot be cancelled twice."""
        registration = RegistrationFactory(
            user=self.visitor, event=self.event, status="cancelled"
        )
        with self.assertRaises(ValueError):
            registration.cancel_registration()

    def test_registration_str_representation(self):
        """Test registration string representation."""
        registration = RegistrationFactory(user=self.visitor, event=self.event)
        expected = f"{self.visitor.email} - {self.event.title}"
        self.assertEqual(str(registration), expected)
