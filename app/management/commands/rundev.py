import os
import subprocess
from django.core.management.base import BaseCommand

file_dir = os.path.dirname(os.path.realpath('__file__'))

def check_env_and_update():
    # checks .env for all the required fields
    # print('Checking Environment Variables...')
    
    envFilePath = os.path.join(file_dir, ".env")
    envCheckerPath = os.path.join(file_dir, "env_check_file")
    
    if not os.path.exists(envFilePath):
        print("The .env file does not exist, you should create it!")
        return False
        
    if not os.path.exists(envCheckerPath):
        os.mknod(envCheckerPath)
        print('env_check_file not found, creating...')
        
    checkerProperties = []
    envProperties = []
    
    # using "with open" ensures that the file gets opened and closed without having to explicitly call f.close()
    with open(envCheckerPath, 'r') as checkerFile, open(envFilePath, 'r') as envFile:
        for check_line in checkerFile.read().splitlines():
            if check_line == "":
                continue

            checkerProperties.append(check_line.strip())
            
        for line in envFile.read().splitlines():
            if line == "":
                continue

            envProperties.append(line.split("=")[0].strip())
            
    for property in checkerProperties:
        # if is empty
        if not property:
            continue
        
        if property not in envProperties:
            print(f".env file missing manditory property {property}")
            return False
              
    with open(envCheckerPath, "+a") as checkerFile:
        # seek to last character of file
        checkerFile.seek(0, os.SEEK_END) 
        checkerFile.seek(checkerFile.tell() - 1, os.SEEK_SET)
        if checkerFile.read(1) != "\n":
            checkerFile.write("\n")
            
        for prop in envProperties:
            if (prop not in checkerProperties):
                print(f"adding {prop} variable to env checker")
                checkerFile.write(prop + "\n")
                
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

        self.stdout.write("Starting Django development server...")
        os.system("python manage.py runserver")
        tailwind_process.terminate()