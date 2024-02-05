### quayside

Welcome to our quayside.app, the project management tool that helps you the question "What's Next?". 

## Setup
You need to install python, pip, and npm (you can do this by installing [Node.js](https://nodejs.org/en/download)). Once that is done, set up your virtual environment (venv):
```bash
python -m venv venv
```
Now activate your venv:
```bash
# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

Then run the following command in this directory to install all dependencies:
```bash
pip install -r requirements.txt
npm install
``` 


## Usage

If your venv has deactivated, reactivate it with the instructions in Setup.
Then to start the development server, run:
```bash
python manage.py rundev
``` 
This custom command will allow you to see add tailwind classes properly (unline `python manage.py runserver`).

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.


If you add any other npm dependencies, please do it by running `npm install --save <my-dependency>` so it is added to package.json for the next person to install. Otherwise, add the package manually to package.json. If you install python dependencies, please add them to the requirements.txt by running `pip freeze > requirements.txt`.

