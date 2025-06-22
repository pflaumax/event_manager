from django.test import TestCase
from django.contrib.auth import get_user_model
from .factories import UserFactory, CreatorFactory, VisitorFactory, EventFactory

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities."""

    def setUp(self):
        """Set up test data."""
        self.creator = CreatorFactory()
        self.visitor = VisitorFactory()

    def assertErrorMessage(self, response, message):
        """Assert that error message is present in response."""
        self.assertContains(response, message)

    def assertRedirectsToLogin(self, response):
        """Assert that response redirects to login page."""
        self.assertRedirects(
            response, "/accounts/login/?next=" + response.wsgi_request.path
        )
