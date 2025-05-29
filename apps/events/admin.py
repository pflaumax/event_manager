from django.contrib import admin
from apps.events.models import Event, Registration

admin.site.register(Event)
admin.site.register(Registration)
