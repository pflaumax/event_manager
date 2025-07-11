from typing import Optional, Iterable
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from apps.events.models import Event, EventRegistration
from apps.users.models import CustomUser
from .forms import CustomUserSignupForm

# Get the user model (settings.py)
User = get_user_model()


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Handle user login via email and password.

    If the request method is POST, attempts to authenticate the user
    using the provided email and password. If authentication is successful,
    the user is logged in and redirected to the index page. If authentication fails,
    an error message is displayed.

    For GET requests, renders the login page.
    Args:
        request (HttpRequest): The incoming HTTP request object.
    Returns:
        HttpResponse: A redirect to the index page on successful login,
                      or a rendered login page on GET request or failed login.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "registration/login.html")


def signup(request: HttpRequest) -> HttpResponse:
    """
    Register a new user with email confirmation.
    Args:
        request: HTTP request object containing user data
    Returns:
        HttpResponse: Rendered registration form or success page
    Behavior:
        - GET: Display empty registration form
        - POST: Process form data and send confirmation email
    """
    if request.method == "POST":
        # Process completed form
        form = CustomUserSignupForm(data=request.POST)

        if form.is_valid():
            # Create user but don't save to a database yet
            new_user: CustomUser = form.save(commit=False)
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
            # If form is invalid show error
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Display a blank registration form
        form = CustomUserSignupForm()

    # Display form
    context = {"form": form}
    return render(request, "registration/signup.html", context)


def activate(request: HttpRequest, uidb64: str, token: str) -> HttpResponseRedirect:
    """
    Activate user accounts when they click the confirmation link in email.
    Args:
        request: HTTP request object
        uidb64: Base64 encoded user ID
        token: Security token for verification
    Returns:
        HttpResponseRedirect: Redirect to login page on success or index on failure
    """
    # Try to decode the user ID and find the user
    user: Optional[CustomUser] = get_user_from_token(uidb64)

    # Check if user exists and the token is valid
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


def send_activation_email(request: HttpRequest, user: CustomUser) -> None:
    """
    Send activation email to new user.
    Args:
        request: HTTP request object for getting current site
        user: User object to send activation email to
    Raises:
        Exception: If email sending fails
    """
    current_site = get_current_site(request)
    subject = "Please activate your account"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    to_email = [user.email]

    # Context for template
    context = {
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
    }

    # Text and HTML versions
    text_content = render_to_string("registration/signup_activation_email.txt", context)
    html_content = render_to_string(
        "registration/signup_activation_email.html", context
    )

    # Create email object
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()


def get_user_from_token(uidb64: str) -> Optional[CustomUser]:
    """
    Safely decode user ID from base64 token and retrieve user.
    Args:
        uidb64: Base64 encoded user ID
    Returns:
        Optional[CustomUser]: User object if found and valid, None otherwise
    """
    try:
        # Decode the user ID from base64
        uid: str = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        return user  # type: ignore[return-value]
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # Return None if any error occurs during decoding/lookup
        return None


def send_event_registration_email(
    request: HttpRequest, registration: EventRegistration
) -> None:
    """
    Send confirmation email when user registers for an event.
    Args:
        request: HTTP request object for getting current site
        registration: EventRegistration object containing user and event details
    Raises:
        Exception: If email sending fails
    """
    current_site = get_current_site(request)
    user: CustomUser = registration.user
    event: Event = registration.event
    subject = f"Registration Confirmed: {event.title}"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    to_email = [user.email]

    # Context for template
    context = {
        "user": user,
        "event": event,
        "registration": registration,
        "domain": current_site.domain,
    }

    # Text and HTML versions
    text_content = render_to_string(
        "registration/event_registration_email.txt", context
    )
    html_content = render_to_string(
        "registration/event_registration_email.html", context
    )

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")

    # Send the email
    try:
        email.send()
        print(f"Registration email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send registration email to {user.email}: {e}")
        raise


def send_event_cancellation_emails(
    request: HttpRequest, event: Event, registrations: Iterable[EventRegistration]
) -> None:
    """
    Send cancellation notification emails to all registered users.
    Args:
        request: HTTP request object for getting current site
        event: Event object that was cancelled
        registrations: Iterable of EventRegistration objects for users to notify
    Raises:
        Exception: If mass email sending fails
    """
    current_site = get_current_site(request)
    from_email: Optional[str] = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    for registration in registrations:
        user = registration.user
        subject = f"Event Cancelled: {event.title}"
        to_email = [user.email]

        # Context for template
        context = {
            "user": user,
            "event": event,
            "registration": registration,
            "domain": current_site.domain,
        }

        # Text and HTML versions
        text_content = render_to_string(
            "registration/event_cancellation_email.txt", context
        )
        html_content = render_to_string(
            "registration/event_cancellation_email.html", context
        )

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")

        # Send the email
        try:
            email.send()
            print(f"Cancellation email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send cancellation email to {user.email}: {e}")
            raise
