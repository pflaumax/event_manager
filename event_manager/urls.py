from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),
    # Welcome page
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    # API URLs
    path("", include("apps.users.urls_api")),  # /api/users/
    path("", include("apps.events.urls_api")),  # /api/events/, /api/registrations/
    # JWT Token endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Regular web views (if you have them)
    path("users/", include("apps.users.urls")),
    path("", include("apps.events.urls")),
]

# Service for upload media files (Debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
