# quayside.app

Welcome to our quayside.app, the project management tool that helps your team answer the question "What's Next?" to succeed in your project goals. The stack is Django with Tailwind and MongoDB. It will hosted on Google Cloud Platform.

## Setup
You need to install python3, pip, and npm (you can do this by installing [Node.js](https://nodejs.org/en/download)). Once that is done, set up your virtual environment (venv):
```bash
python -m venv venv
```
Now activate your venv:
```bash
# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Windows Bash:
source venv\Scripts\activate
```

Then run the following command in this directory to install all dependencies:
```bash
pip install -r requirements.txt
npm install
``` 

For accessing the mongo database locally, you will need the following generated database Atlas, ChatGPT, and Github creds in an `.env` file (fyi, the Atlas creds are different than your creds to login to Mongo Atlas). You'll also need the following Github URLs. Here is the format:

```bash
MONGO_USERNAME=<your username>
MONGO_PASSWORD=<your password>
CHATGPT_API_KEY=<your ChatGPT API key>
GITHUB_CLIENT_ID=<your client ID>
GITHUB_CLIENT_SECRET =<your client secret>
GITHUB_API_URL_email=https://api.github.com/user/emails
GITHUB_API_URL_user=https://api.github.com/user
```


## Usage

If your venv has deactivated, reactivate it with the instructions in Setup.
Then to start the development server, run:
```bash
python manage.py rundev
``` 
This custom command will allow you to see add tailwind classes properly (unlike `python manage.py runserver`).

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) with your browser to see the result.



If you add any other npm dependencies, please do it by running `npm install --save <my-dependency>` so it is added to package.json for the next person to install. Otherwise, add the package manually to package.json. If you install python dependencies, please add them to the requirements.txt by running `pip freeze > requirements.txt`.

