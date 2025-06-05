from django.contrib import admin
from django.urls import path, include
from . import views

# import debug_toolbar

urlpatterns = [
    # path("__debug__/", include(debug_toolbar.urls)),
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("users/", include("apps.users.urls")),
    path("", include("apps.events.urls")),
]
