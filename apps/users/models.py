from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model.
    Responsible for creating regular users and superusers.
    """

    def create_user(self, email, full_name, password=None, role="visitor"):
        """
        Create and save a new user with the given email, full name, password,
        and role.
        """
        if not email:
            raise ValueError("Users must have an email address")
        if not full_name:
            raise ValueError("Users must have a full name or pseudonym")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None):
        """Create and save a new superuser with all permissions."""
        user = self.create_user(email, full_name, password, role="creator")
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
        unique=True, blank=False, null=False, help_text="Email address used for login"
    )
    full_name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z\s\-\'\.]+$",
                message="Full name can only contain letters, spaces, hyphens, apostrophes, and periods.",
            )
        ],
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_TYPE_CHOICES,
        default="visitor",
        blank=False,
        null=False,
        help_text="User role determines permissions",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

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

    """def cancel_event(self, user):
        # Allow only the creator to cancel the event.
        if self.is_visitor:
            raise PermissionError("Only the event creator can cancel this event.")
        if self.status != "published":
            raise ValueError("Only published events can be cancelled.")
        self.status = "cancelled"
        self.save()"""
