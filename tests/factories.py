import factory
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from apps.events.models import Event, EventRegistration

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    is_active = True


class CreatorFactory(UserFactory):
    role = "creator"


class VisitorFactory(UserFactory):
    role = "visitor"


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Sequence(lambda n: f"Test Event {n}")
    description = "Test event description"
    location = "Test Location"
    date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=7))
    creator = factory.SubFactory(CreatorFactory)
    status = "published"


class PastEventFactory(EventFactory):
    date = factory.LazyFunction(lambda: datetime.now() - timedelta(days=7))
    status = "completed"


class RegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventRegistration

    user = factory.SubFactory(VisitorFactory)
    event = factory.SubFactory(EventFactory)
    status = "registered"
