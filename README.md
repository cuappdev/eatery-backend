# eatery-backend
An open-sourced backend for the Eatery application, available on Android and iOS.

Technologies involved include:
1. Flask
2. GraphQL

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
