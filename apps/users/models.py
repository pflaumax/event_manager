from typing import Optional
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model with email-based authentication.

    This manager is responsible for creating regular users and superusers
    with proper validation and default role assignment.
    """

    def create_user(
        self,
        email: str,
        username: str,
        password: Optional[str] = None,
        role: str = "visitor",
    ) -> "CustomUser":
        """
        Create and save a new user with the given email, username, password, and role.
        Args:
            email: User's email address (required)
            username: User's username or event pseudonym (required)
            password: User's password (optional)
            role: User's role, defaults to "visitor"
        Returns:
            CustomUser: The created user instance
        Raises:
            ValueError: If email or username is not provided
        """
        if not email:
            raise ValueError("Users must have an email address.")
        if not username:
            raise ValueError("Users must have a username or event pseudonym.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, username: str, password: Optional[str] = None
    ) -> "CustomUser":
        """
        Create and save a new superuser with all permissions.
        Args:
            email: Superuser's email address (required)
            username: Superuser's username (required)
            password: Superuser's password (optional)
        Returns:
            CustomUser: The created superuser instance
        """
        user = self.create_user(email, username, password, role="creator")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email authentication and role-based access.

    This model extends Django's AbstractBaseUser to provide email-based
    authentication instead of username-based authentication, along with
    role-based permissions for visitors and event creators.
    """

    ROLE_TYPE_CHOICES: tuple[tuple[str, str], ...] = (
        ("visitor", "Visitor"),
        ("creator", "Event Creator"),
    )

    email: models.EmailField = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        help_text="User's email address used for authentication",
    )

    username: models.CharField = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(
                3, message="Username must be at least 3 characters long."
            )
        ],
        help_text="User's display name or event pseudonym",
    )

    role: models.CharField = models.CharField(
        max_length=10,
        choices=ROLE_TYPE_CHOICES,
        default="visitor",
        blank=False,
        null=False,
        help_text="User's role determining their permissions",
    )

    is_active: models.BooleanField = models.BooleanField(
        default=False,
        help_text="Designates whether this user should be treated as active. "
        "Set to True after email confirmation.",
    )
    is_staff: models.BooleanField = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )
    date_joined: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the user account was created"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Use email instead of username for login
    REQUIRED_FIELDS = ["username"]  # Username required for superuser creation

    class Meta:
        """
        Model metadata configuration.
        Sets verbose names for admin display and adds database indexes
        for faster lookup by email and role fields.
        """

        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of the user.
        Returns:
            str: Formatted string with username, email, and role
        """
        return f"{self.username} ({self.email}) - {self.role}"

    def clean(self) -> None:
        """
        Perform custom validation for the CustomUser model.
        Validates that the username contains at least one alphanumeric character
        after stripping whitespace.
        Raises:
            ValidationError: If username doesn't contain alphanumeric characters
        """
        super().clean()
        if self.username:
            self.username = self.username.strip()
            if not any(char.isalnum() for char in self.username):
                raise ValidationError(
                    {"username": "Username must include at least one letter or number."}
                )

    @property
    def is_creator(self) -> bool:
        """
        Check if user has a creator role.
        Returns:
            bool: True if a user is an event creator, False otherwise
        """
        return self.role == "creator"

    @property
    def is_visitor(self) -> bool:
        """
        Check if a user has a visitor role.
        Returns:
            bool: True if the user is a visitor, False otherwise
        """
        return self.role == "visitor"

    def can_create_events(self) -> bool:
        """
        Check if user has permission to create events.
        Returns:
            bool: True if user can create events, False otherwise
        """
        return self.is_creator

    def can_register_for_events(self) -> bool:
        """
        Check if user has permission to register for events.
        Returns:
            bool: True if user can register for events, False otherwise
        """
        return self.is_visitor
