from django.urls import path
from . import views

appname = "users"
urlpatterns = [
    # Page for user registration
    path("signup/", views.signup, name="signup"),
    # Page for user registration
    # path("register/", views.register, name="register"),
]
