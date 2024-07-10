# quayside.app

Welcome to our quayside.app, the project management tool that helps your team answer the question "What's Next?" to succeed in your project goals. The stack is Django with Tailwind and PostgreSQL. It is hosted on Google Cloud Platform.

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

Then run these following commands in this directory to install all dependencies:

```bash
pip install -r requirements.txt
```

```bash
npm install
```

For accessing the mongo database locally, you will need the following generated database Atlas, ChatGPT, and Github creds in an `.env` file (fyi, the Atlas creds are different than your creds to login to Mongo Atlas). You'll also need the following Github URLs. Check the env\_check\_file for the required variables.

**PostgresSQL** <br>
In order to access the Google Cloud postgress DB, you will need to add your IP to the allowed networks in Google Cloud.

**On the production server**, remove GOOGLE_APPLICATION_CREDENTIALS, set the correct BASE_URL domain, set DEBUG=False, and set GOOGLE_POSTGRES_HOST to `/cloudsql/<PROJECT_ID>:<REGION>:<INSTANCE_ID>` (/cloudsql/elevare-data-website:us-west1:elevare-data-postgress). In the production server, you will need the STRIPE_WEBHOOK key from stripes website when you set up the webhook (https://docs.stripe.com/webhooks).



## Usage

**Running** <br>
If your venv has deactivated, reactivate it with the instructions in Setup.
Then to start the development server, run:

```bash
python manage.py rundev
```

This custom command will allow you to see add tailwind classes properly (unlike `python manage.py runserver`).

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) with your browser to see the result.

**Linting** <br>
We use pep8 and JavaScript Standard Style standards. The only exceptions to these are that we use camelCase and jsdocs function block strings for python as well as javascript. We use black and pylint for our python and eslint for our javascript. Here's the commands to run to lint your code:

```bash
# Automagically reformats your python code.
black app api

# Reports potential python bugs/errors. Fix as many of them as you can (get a score of 8.+).
pylint app/ api/

# Fixes as many javascript formatting/code errors as possible and tells you which ones you heed to fix yourself.
npx eslint app/**/*.html --fix
```

Note: If npx tells you `<someFunction> is not defined  no-undef` because someFunction is defined in a script you are importing, add the following comment before each line where the error occurs.
```js
// eslint-disable-next-line no-undef
```



**Adding Dependencies** <br>
If you add any other npm dependencies, please do it by running `npm install --save <my-dependency>` so it is added to package.json for the next person to install. Otherwise, add the package manually to package.json. If you install python dependencies, please add them to the requirements.txt by running `pip freeze > requirements.txt`.

Note: If you are having issues with "[SSL: CERTIFICATE_VERIFY_FAILED]" you may need to upgrade pip.

**Changing Models** <br>
If you change models, run

```bash
python manage.py makemigrations
python manage.py migrate
```
