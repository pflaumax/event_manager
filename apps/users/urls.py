from django.urls import path, include
from . import views


app_name = "users"
urlpatterns = [
    # Login page
    path("login/", views.login_view, name="login"),
    # Registration page
    path("sign_up/", views.signup, name="signup"),
    # Include default auth urls (login)
    path("", include("django.contrib.auth.urls")),
    # Account activation
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
]
