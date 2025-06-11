from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .forms import CustomUserSignupForm

# Get the user model (settings.py)
User = get_user_model()


def signup(request):
    """
    Register a new user with email confirmation.
    GET: Display empty registration form.
    POST: Process form data and send confirmation email.
    """
    if request.method == "POST":
        # Process completed form
        form = CustomUserSignupForm(data=request.POST)

        if form.is_valid():
            # Create user but don't save to database yet
            new_user = form.save(commit=False)
            new_user.is_active = False  # User must confirm email first
            new_user.save()

            # Send confirmation email
            send_activation_email(request, new_user)
            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return render(request, "index.html")
    else:
        # Display blank registration form
        form = CustomUserSignupForm()

    # Display form
    context = {"form": form}
    return render(request, "registration/signup.html", context)


def activate(request, uidb64, token):
    """
    Activate user account when they click the confirmation link in email.
    uidb64: Base64 encoded user ID.
    token: Security token for verification.
    """
    # Try to decode the user ID and find the user
    user = get_user_from_token(uidb64)
    # Check if user exists and token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # Activate the user account
        user.is_active = True
        user.save()

        messages.success(
            request, "Your account has been activated successfully! You can now log in."
        )
        return redirect("users:login")
    else:
        # Invalid or expired link
        messages.error(
            request,
            "The activation link is invalid or has expired. Please try registering again.",
        )
        return redirect("index")


def send_activation_email(request, user):
    """
    Helper function to send activation email to new user.
    Request: HTTP request object.
    User: User object to send email to.
    """
    current_site = get_current_site(request)
    subject = "Please activate your account"

    # Create the email message from template
    message = render_to_string(
        "registration/signup_activation.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )

    # Send the email
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    send_mail(subject, message, from_email, [user.email])


def get_user_from_token(uidb64):
    """
    Helper function to safely decode user ID from base64 token.
    idb64: Base64 encoded user.
    returns user object if found, None otherwise.
    """
    try:
        # Decode the user ID from base64
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # Return None if any error occurs during decoding/lookup
        return None
