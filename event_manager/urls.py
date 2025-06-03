from django.contrib import admin
from django.urls import path, include
from . import views
import debug_toolbar

urlpatterns = [
    path("__debug__/", include(debug_toolbar.urls)),
    path("admin/", admin.site.urls),
    path("", include("apps.users.urls")),
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
]
