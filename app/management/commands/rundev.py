import os
import subprocess
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """Starts Tailwind CSS build process and Django server for development.
        Run instead of runserver when editing tailwind components."""

    def handle(self, *args, **options):
        self.stdout.write("Starting Tailwind CSS build process...")
        tailwind_process = subprocess.Popen(
            # ['npx', 'tailwindcss', '-i', './app/static/app/src/input.css', '-o', './app/static/app/src/output.css', '--watch'],
            # String required when shell=True (less safe though)
            "npx tailwindcss -i ./app/static/app/src/input.css -o ./app/static/app/src/output.css --watch",
            shell=True,
        )

        self.stdout.write("Starting Django development server...")
        os.system("python manage.py runserver")
        tailwind_process.terminate()
