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
from apps.events.models import EventRegistration


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
        elif self.action == "my_registrations":
            return MyRegistrationsSerializer
        return UserRegistrationSerializer

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserProfileSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """Login user and return JWT tokens."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "user": UserProfileSerializer(user).data,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )
            else:
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["get", "put", "patch"],
        permission_classes=[IsAuthenticated],
    )
    def profile(self, request):
        """Get or update user profile."""
        if request.method == "GET":
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)

        elif request.method in ["PUT", "PATCH"]:
            serializer = UserProfileSerializer(
                request.user, data=request.data, partial=(request.method == "PATCH")
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_registrations(self, request):
        """Get current user's event registrations."""
        if request.user.role != "visitor":
            return Response(
                {"detail": "Only Visitors have event registrations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        registrations = EventRegistration.objects.filter(user=request.user)
        serializer = MyRegistrationsSerializer(registrations, many=True)
        return Response(serializer.data)
