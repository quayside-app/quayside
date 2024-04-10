#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def check_env():
    # checks .env for all the required fields
    # print('Checking Environment Variables...')
    env_file = open('.env')
    env_check_file = open('env_check_file')
    for check_line in env_check_file:
        LINE_EXISTS = False
        check_line = check_line.partition("\n")[0]
        for env_line in env_file:
            if check_line in env_line:
                LINE_EXISTS = True
                break
        if not(LINE_EXISTS):
            print(f".env file missing variable {check_line}")

def check_env_updater():
    # automatically updates env_check_file with all the variables from .env
    # print('Updating env_check_file...')
    env_file = open('.env')
    env_check_file = open('env_check_file')
    for env_line in env_file:
        LINE_EXISTS = False
        env_line = env_line.partition("=")[0]
        env_line = env_line.partition(" ")[0]
        for check_line in env_check_file:
            if env_line in check_line:
                LINE_EXISTS = True
                break
        if LINE_EXISTS == False:
            print(f"adding {env_line} variable to env checker")
            with open('env_check_file', 'a') as file:
                file.write(env_line + "\n")





def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quayside.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    check_env()
    check_env_updater()
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
