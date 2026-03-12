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

Then run these following commands in this directory to install all dependencies:

```bash
pip install -r requirements.txt
```

```bash
npm install
```

For accessing the mongo database locally, you will need the following generated database Atlas, ChatGPT, and Github creds in an `.env` file (fyi, the Atlas creds are different than your creds to login to Mongo Atlas). You'll also need the following Github URLs. Here is the format:

```bash
MONGO_USERNAME=<your username>
MONGO_PASSWORD=<your password>
CHATGPT_API_KEY=<your ChatGPT API key>
GITHUB_CLIENT_ID=<your client ID>
GITHUB_CLIENT_SECRET=<your client secret>
GITHUB_API_URL_email=https://api.github.com/user/emails
GITHUB_API_URL_user=https://api.github.com/user
GOOGLE_CLIENT_ID=<your Google OAuth client ID>
GOOGLE_CLIENT_SECRET=<your Google OAuth client secret>
GOOGLE_API_URL_userprofile=https://www.googleapis.com/oauth2/v1/userinfo
API_SECRET=<key you make up to encrypt your jwt tokens (must be 32 url-safe base64-encoded bytes)>
REDIRECT_URI=<your OAuth redirect URI, e.g. http://127.0.0.1:8000/auth/callback>
DEBUG_BOOL=True
GOOGLE_POSTGRES_HOST=<your Cloud SQL host>
GOOGLE_POSTGRES_USER=<your Cloud SQL user>
GOOGLE_POSTGRES_PASSWORD=<your Cloud SQL password>
```

See [`env_check_file`](env_check_file) for the full list of required variables.
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

## AI-Assisted Development

This repo is configured for use with [Claude Code](https://claude.ai/claude-code). The [`CLAUDE.md`](CLAUDE.md) file at the root defines how AI agents should work in this codebase — conventions, code review standards, git workflow, and more. If you're using Claude Code, it will pick this up automatically.

Additional resources for AI-assisted workflows:
- [`docs/specs/spec-writing-guidelines.md`](docs/specs/spec-writing-guidelines.md) — how to write implementation specs before building something significant
- [`docs/decisions/template.md`](docs/decisions/template.md) — ADR template for recording architectural decisions
- `.claude/skills/` — reusable Claude Code skills (e.g. `/gen-release-notes`)
