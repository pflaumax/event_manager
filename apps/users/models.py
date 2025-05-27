from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model.
    Responsible for creating regular users and superusers.
    """

    def create_user(self, email, full_name, password=None, role="visitor"):
        """
        Create and save a new user with the given email, full name, password, and role.
        """
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None):
        """
        Create and save a new superuser with all permissions.
        """
        user = self.create_user(email, full_name, password, role="creator")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email authentication.
    """

    ROLE_TYPE_CHOICES = (
        ("creator", "Creator"),
        ("visitor", "Visitor"),
    )

    email = models.EmailField(unique=True, blank=False, null=False)
    full_name = models.CharField(max_length=60, blank=False, null=False)
    role = models.CharField(
        max_length=10,
        choices=ROLE_TYPE_CHOICES,
        default="visitor",
        blank=False,
        null=False,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.full_name
