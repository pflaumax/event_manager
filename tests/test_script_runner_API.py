#!/usr/bin/env python
"""
Simple script to run API tests for the Event Management System.
Usage: python run_tests.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings


def run_tests():
    """Run the API tests."""
    print("Setting up Django environment...")

    # Setup Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    print("Running API tests...\n")

    # Run specific test classes
    test_commands = [
        "test apps.users.tests.UserAPITests",
        "test apps.events.tests.EventAPITests",
        "test apps.events.tests.EventRegistrationAPITests",
    ]

    for command in test_commands:
        print(f"Running: {command}")
        execute_from_command_line(["manage.py"] + command.split())
        print("-" * 50)


if __name__ == "__main__":
    run_tests()

# Alternative: Simple Django management command
# Create this file as: management/commands/run_api_tests.py

from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner


class Command(BaseCommand):
    help = "Run API tests for Event Management System"

    def handle(self, *args, **options):
        """Run the tests."""
        test_runner = DiscoverRunner(verbosity=2, interactive=True)

        test_modules = [
            "apps.users.tests.UserAPITests",
            "apps.events.tests.EventAPITests",
            "apps.events.tests.EventRegistrationAPITests",
        ]

        failures = test_runner.run_tests(test_modules)

        if failures:
            self.stdout.write(self.style.ERROR(f"{failures} test(s) failed!"))
        else:
            self.stdout.write(self.style.SUCCESS("All tests passed!"))
