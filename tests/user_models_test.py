from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from tests.factories import UserFactory, CreatorFactory, VisitorFactory

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""

    def test_create_user_with_valid_data(self):
        """Test creating user with valid data."""
        user = UserFactory()
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_creator_user(self):
        """Test creating user with creator role."""
        creator = CreatorFactory()
        self.assertEqual(creator.role, "creator")
        self.assertFalse(creator.is_staff)

    def test_create_visitor_user(self):
        """Test creating user with visitor role."""
        visitor = VisitorFactory()
        self.assertEqual(visitor.role, "visitor")
        self.assertFalse(visitor.is_staff)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = UserFactory(username="user4", email="test@example.com", role="visitor")
        expected_str = "user4 (test@example.com) - visitor"
        self.assertEqual(str(user), expected_str)

    def test_create_user_with_empty_email(self):
        """Test that creating user with empty email raises ValidationError."""
        with self.assertRaises(ValidationError):
            user = User(email="", username="testuser", role="visitor")
            user.full_clean()

    def test_create_user_with_invalid_email(self):
        """Test that creating user with invalid email raises ValidationError."""
        with self.assertRaises(ValidationError):
            user = User(email="invalid-email", username="testuser", role="visitor")
            user.full_clean()

    def test_email_uniqueness(self):
        """Test that duplicate emails are not allowed."""
        UserFactory(email="test@example.com")
        with self.assertRaises(ValidationError):
            user = User(email="test@example.com", username="testuser2", role="visitor")
            user.full_clean()
