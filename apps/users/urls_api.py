from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import CustomUserViewSet

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("api/", include(router.urls)),
]
