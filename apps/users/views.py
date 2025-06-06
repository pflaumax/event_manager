from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserSignupForm


def signup(request):
    """Register a new user."""
    if request.method != "POST":
        # Display blank registration form
        form = CustomUserSignupForm()
    else:
        # Process completed form
        form = CustomUserSignupForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            # Log the user in and then redirect to home page
            login(request, new_user)
            return redirect("home")

    # Display a blank or invalid form
    context = {"form": form}
    return render(request, "registration/signup.html", context)
