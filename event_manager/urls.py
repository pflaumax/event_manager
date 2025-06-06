from django.contrib import admin
from django.urls import path, include
from . import views
import debug_toolbar

urlpatterns = [
    # Debug toolbar
    # path("__debug__/", include(debug_toolbar.urls)),
    # Admin panel for superusers
    path("admin/", admin.site.urls),
    # Welcome page
    path("", views.index, name="index"),
    # Homepage after login/registration
    path("home/", views.home, name="home"),
    # User-related routes (login, registration)
    path("users/", include("apps.users.urls")),
    # Event-related routes (creating, viewing)
    path("", include("apps.events.urls")),
]
