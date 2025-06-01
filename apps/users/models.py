from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model. Email-based authentication.
    Responsible for creating regular users and superusers.
    """

    def create_user(self, email, username, password=None, role="visitor"):
        """
        Create and save a new user with the given email,
        username, password, and role.
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

    def create_superuser(self, email, username, password=None):
        """Create and save a new superuser with all permissions."""
        user = self.create_user(email, username, password, role="creator")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email authentication and role-based access."""

    ROLE_TYPE_CHOICES = (
        ("creator", "Event Creator"),
        ("visitor", "Visitor"),
    )

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        help_text="Email address used for login.",
    )

    username = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(3, message="Title must be at least 3 characters long.")
        ],
        help_text="Enter your name, group name or pseudonym.",
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_TYPE_CHOICES,
        default="visitor",
        blank=False,
        null=False,
        help_text="User role determines permissions.",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Use email instead username for login by default
    REQUIRED_FIELDS = ["username"]  # Username required for superuser creation

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email}), {self.role}"

    def clean(self):
        """Perform custom username validation for the CustomUser model."""
        super().clean()
        if self.username:
            self.username = self.username.strip()
            if not any(char.isalnum() for char in self.username):
                raise ValidationError(
                    "Name must include at least one letter or number."
                )

    @property
    def is_creator(self):
        """Check if user is an event creator."""
        return self.role == "creator"

    @property
    def is_visitor(self):
        """Check if user is a visitor."""
        return self.role == "visitor"

    def can_create_events(self):
        """Check if user can create events."""
        return self.is_creator

    def can_register_for_events(self):
        """Check if user can register for events."""
        return self.is_visitor
