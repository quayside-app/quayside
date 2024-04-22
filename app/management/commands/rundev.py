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
        check_env()
        check_env_updater()
        self.stdout.write("Starting Django development server...")
        os.system("python manage.py runserver")
        tailwind_process.terminate()


def check_env():
    # checks .env for all the required fields
    # print('Checking Environment Variables...')
    env_file = open(".env")
    env_check_file = open("env_check_file")
    for check_line in env_check_file:
        LINE_EXISTS = False
        check_line = check_line.partition("\n")[0]
        for env_line in env_file:
            if check_line in env_line:
                LINE_EXISTS = True
                break
        if not LINE_EXISTS:
            print(f".env file missing variable {check_line}")


def check_env_updater():
    # automatically updates env_check_file with all the variables from .env
    # print('Updating env_check_file...')
    env_file = open(".env")
    env_check_file = open("env_check_file")
    for env_line in env_file:
        LINE_EXISTS = False
        env_line = env_line.partition("=")[0]
        env_line = env_line.partition(" ")[0]
        for check_line in env_check_file:
            if env_line in check_line:
                LINE_EXISTS = True
                break
        if not LINE_EXISTS:
            print(f"adding {env_line} variable to env checker")
            with open("env_check_file", "a") as file:
                file.write(env_line + "\n")
