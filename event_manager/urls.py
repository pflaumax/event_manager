from django.contrib import admin
from django.urls import path, include
from . import views

# import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Debug toolbar
    # path("__debug__/", include(debug_toolbar.urls)),
    # Admin panel for superusers
    path("admin/", admin.site.urls),
    # Welcome page
    path("", views.index, name="index"),
    # Homepage after login/registration
    path("home/", views.home, name="home"),
    # Users API URL page
    path("api/users", include("apps.users.urls_api")),
    # User-related routes (login, registration)
    path("users/", include("apps.users.urls")),
    # Event-related routes (creating, viewing)
    path("", include("apps.events.urls")),
    # Event API URL page
    path("", include("apps.events.urls_api")),
]

# Service for upload media files (Debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
