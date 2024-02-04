### quayside

Welcome to our quayside.app, the project management tool that helps you the question "What's Next?". 

## Setup
You need to install python and npm (you can do this by installing [Node.js](https://nodejs.org/en/download)). Once that is done, set up your virtual environment and activate it.

Mac/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Then run the following command in this directory to install all dependencies:
```bash
python -r requirements.txt
npm install
``` 


## Usage

To run the developlement server, run:
```bash
python manage.py rundev
``` 
This custom command will allow you to see add tailwind classes properly (unline `python manage.py runserver`).

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.


If you add any other npm dependencies, please do it by running `npm install --save <my-dependency>` so it is added to package.json for the next person to install. Otherwise, add the package manually to package.json. If you install python dependencies, please add them to the requirements.txt by running `pip freeze > requirements.txt`.

