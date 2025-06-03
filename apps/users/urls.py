from django.urls import path
from . import views

appname = "users"
urlpatterns = [
    # Page for user registration
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    # Page for user registration
    # path("register/", views.register, name="register"),
]
