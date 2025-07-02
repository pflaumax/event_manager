from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from typing import Any
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    LoginSerializer,
    MyRegistrationsSerializer,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""

    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    def get_permissions(self):
        """Return permissions based on action."""
        if self.action in ["create", "register", "login"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ["retrieve", "update", "partial_update", "profile"]:
            return UserProfileSerializer
        elif self.action == "login":
            return LoginSerializer
        return UserRegistrationSerializer


class UserRegistrationViewSet(viewsets.ModelViewSet):
    # queryset = CustomUser.objects.all()
    serializer_class = [AllowAny]


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
