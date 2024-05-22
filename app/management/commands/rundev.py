import os
import subprocess
from django.core.management.base import BaseCommand

file_dir = os.path.dirname(os.path.realpath('__file__'))

def check_env_and_update():
    # checks .env for all the required fields
    # print('Checking Environment Variables...')
    
    env_file_path = os.path.join(file_dir, ".env")
    env_checker_path = os.path.join(file_dir, "env_check_file")
    
    if not os.path.exists(env_file_path):
        print("The .env file does not exist, you should create it!")
        return False
        
    if not os.path.exists(env_checker_path):
        os.mknod(env_checker_path)
        print('env_check_file not found, creating...')
        
    checker_properties = []
    env_properties = []
    
    # using "with open" ensures that the file gets opened and closed without having to explicitly call f.close()
    with open(env_checker_path, "r") as checker_file, open(env_file_path, 'a+') as env_file:
        for check_line in checker_file.read().splitlines():
            if check_line == "":
                continue

            checker_properties.append(check_line.strip())
            
        for i, line in enumerate(env_file.read().splitlines()):
            if line == "":
                continue

            env_properties.append(line.split("=")[0].strip())
            
    for property in checker_properties:
        # if is empty
        if not property:
            continue
        
        if property not in env_properties:
            print(f".env file missing manditory {property}")
            return False
              
    with open(env_checker_path, '+a') as f:
        for prop in env_properties:
            if (prop not in checker_properties):
                print(f"adding {prop} variable to env checker")
                f.write(prop + "\n")
                
    return True

class Command(BaseCommand):
    help = """Starts Tailwind CSS build process and Django server for development.
        Run instead of runserver when editing tailwind components."""

    def handle(self, *args, **options):
        if (not check_env_and_update()):
            exit()
            
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
