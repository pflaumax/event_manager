from django.urls import path, include
from . import views


app_name = "users"
urlpatterns = [
    # Include default auth urls (login)
    path("", include("django.contrib.auth.urls")),
    # Registration page
    path("sign_up/", views.signup, name="signup"),
    # Account activation
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
]
