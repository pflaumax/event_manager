from typing import Optional
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

User = get_user_model()


class EmailBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in using their email address and password.
    """

    def authenticate(
        self,
        request: Optional[HttpRequest],
        email: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ) -> Optional[AbstractBaseUser]:
        """
        Authenticate user using email and password.

        :param request: Django HttpRequest object (can be None).
        :param email: Email address of the user.
        :param password: Password provided by the user.
        :return: User object if authentication is successful, otherwise None.
        """
        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

        return None
