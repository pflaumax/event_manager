from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import CustomUserViewSet

router = DefaultRouter()
router.register(r"", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
