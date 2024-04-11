import os
import subprocess
from django.core.management.base import BaseCommand

def check_env():
    # checks .env for all the required fields
    # print('Checking Environment Variables...')
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    try:
        env_file = open(os.path.join(file_dir,'.env'))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
                "The .env file does not exist, you should create it!"
                ) from exc
        exit()
    try:
        env_check_file = open(os.path.join(file_dir,'env_check_file'))
    except FileNotFoundError:
        print('env_check_file not found, creating...')
        env_check_file = open(os.path.join(file_dir,'env_check_file'), 'x')
        env_check_file = open(os.path.join(file_dir,'env_check_file'))
    counter = 0
    for check_line in env_check_file:
        counter += 1
        LINE_EXISTS = False
        check_line = check_line.replace("\n","")
        check_line = check_line.replace(" ","")
        if check_line == "":
            continue
        env_file_lines = open(os.path.join(file_dir,'.env'))
        for env_line in env_file_lines:
            if env_line.replace(" ","").replace("\n","") == "":
                continue
            if check_line in env_line.partition("=")[0]:
                LINE_EXISTS = True
                break
        if LINE_EXISTS == False:
            print(f".env file missing variable {check_line}")

def check_env_updater():
    # automatically updates env_check_file with all the variables from .env
    # print('Updating env_check_file...')
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    env_file = open(os.path.join(file_dir,'.env'))
    env_check_file = open(os.path.join(file_dir,'env_check_file'))
    for env_line in env_file:
        LINE_EXISTS = False
        env_line = env_line.partition("=")[0]
        env_line = env_line.replace(" ","")
        env_line = env_line.replace("\n","")
        if env_line == "":
            continue
        env_check_file_lines = open(os.path.join(file_dir,'env_check_file'))
        for check_line in env_check_file_lines:
            if (env_line in check_line):
                LINE_EXISTS = True
                break
        if LINE_EXISTS == False:
            print(f"adding {env_line} variable to env checker")
            with open(os.path.join(file_dir,'env_check_file'), 'a') as file:
                file.write(env_line + "\n")

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
