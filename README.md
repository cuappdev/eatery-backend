# eatery-backend
An open-sourced backend for the Eatery application, available on Android and iOS.

Technologies involved include:
1. Flask
2. GraphQL
3. SQLAlchemy

## Virtualenv

Virtualenv setup!

```bash
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables
It's recommended to use [`direnv`](https://direnv.net).
The required environment variables for this API are the following:

To use `direnv` with this repository, run the following and set the variables appropriately.

```bash
cp envrc.template .envrc
```

## Running the App

```bash
sh start_server.sh
```

## GraphQL Interface

The flask app runs on your ['localhost'](http://localhost:5000/) via port 5000.

------------------
## Setting up linter
**Flake 8**: Install [flake8](http://flake8.pycqa.org/en/latest/)

**Black**: Either use [command line tool](https://black.readthedocs.io/en/stable/installation_and_usage.html) or use [editor extension](https://black.readthedocs.io/en/stable/editor_integration.html). 

If using VS Code, install the 'Python' extension and include following snippet inside `settings.json`:
```  json
"python.linting.pylintEnabled": false,
"python.linting.flake8Enabled": true,
"python.formatting.provider": "black"
 ```
