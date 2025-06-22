from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tests.base import BaseTestCase
from tests.factories import (
    CreatorFactory,
    VisitorFactory,
    EventFactory,
    RegistrationFactory,
)
from apps.events.models import Event, EventRegistration
from event_manager import settings

User = get_user_model()


class EventViewTest(BaseTestCase):
    """Test cases for Event views."""

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_event_list_view_anonymous(self):
        """Test event list view for anonymous users."""
        EventFactory.create_batch(3)
        url = reverse("events:browse_events")
        response = self.client.get(url)
        expected_redirect = f"{reverse(settings.LOGIN_URL)}?next={url}"
        self.assertRedirects(response, expected_redirect)

    def test_event_list_view_visitor(self):
        """Test event list view for visitors."""
        self.client.force_login(self.visitor)
        EventFactory.create_batch(3)
        response = self.client.get(reverse("events:browse_events"))
        self.assertEqual(response.status_code, 200)

    def test_event_detail_view(self):
        """Test event detail view."""
        event = EventFactory()
        url = reverse("events:event_details", args=[event.pk])
        response = self.client.get(url)
        expected_redirect = f"{reverse(settings.LOGIN_URL)}?next={url}"
        self.assertRedirects(response, expected_redirect)

    def test_event_create_view_creator(self):
        """Test event creation view for creators."""
        self.client.force_login(self.creator)
        response = self.client.get(reverse("events:new_event"))
        self.assertEqual(response.status_code, 200)

    def test_register_for_event_visitor(self):
        """Test visitor registration for event."""
        self.client.force_login(self.visitor)
        event = EventFactory()
        response = self.client.post(
            reverse("events:register_for_event", args=[event.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EventRegistration.objects.filter(user=self.visitor, event=event).exists()
        )

    def test_register_for_event_creator(self):
        """Test that creator cannot register for event."""
        event = EventFactory()
        url = reverse("events:register_for_event", args=[event.pk])
        response = self.client.post(url)
        expected_redirect = f"{reverse(settings.LOGIN_URL)}?next={url}"
        self.assertRedirects(response, expected_redirect)

    def test_cancel_registration(self):
        """Test canceling registration."""
        self.client.force_login(self.visitor)
        registration = RegistrationFactory(user=self.visitor)
        response = self.client.post(
            reverse("events:cancel_registration", args=[registration.pk])
        )
        self.assertEqual(response.status_code, 302)
        registration.refresh_from_db()
        self.assertEqual(registration.status, "cancelled")
