from django.contrib import admin
from django.urls import path, include
from . import views
import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
    path("", include("apps.users.urls")),
    # Home page
    path("home/", views.home, name="home"),
]
