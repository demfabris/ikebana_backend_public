# Ikebana Backend Public

This is a RESTful Flask application using uWSGI and NGINX for serving...
I'm making this public to help other devs using this stack

## :computer: Features

* [Docker](https://www.docker.com/)
* [uWSGI](https://uwsgi-docs.readthedocs.io/)
* [NGINX](https://www.nginx.com/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Flask](https://flask.palletsprojects.com/)

## :pen: Project structure

```
.
├── docker-compose.yml
├── flask
│   ├── Dockerfile
│   ├── app
│   │   ├── __init__.py
│   │   ├── common
│   │   │   ├── __init__.py
│   │   │   ├── email.py
│   │   │   ├── hashing.py
│   │   │   ├── jwt.py
│   │   │   ├── models.py
│   │   │   ├── notifications.py
│   │   │   └── uploads.py
│   │   ├── config.py
│   │   ├── resources
│   │   │   ├── __init__.py
│   │   │   ├── content_manager.py
│   │   │   ├── oauth.py
│   │   │   └── user_auths.py
│   │   └── storage
│   │       ├── content.db
│   │       └── users.db
│   ├── requirements.txt
│   ├── testing.py
│   ├── wsgi.ini
│   └── wsgi.py
└── nginx
    ├── Dockerfile
    ├── nginx.conf
    ├── self-signed.conf
    ├── setup.sh
    ├── ssl-params.conf
    └── webapp.conf
```

## :steam_locomotive: Installation

`git clone git@github.com:fabricio7p/Ikebana-Backend-Public`

### Setting flask app env variables:

Head into flask folder, open dockerfile and set your variables.
You might wan't to change email addresses and oauth redirects at it's respective python files

**If you wish to run outside docker**:
`pipenv install -r requirements.txt`

### Setting up NGINX

Head into nginx folder and: `./setup.sh`
**Please note that ssl support requires aditional .crt and .key files (Check dockerfile for more info)**

### Run
In project root directory:
`docker-compose build | docker-compose up`

## :thinking: Final considerations
This project is live at https://api.fabricio7p.com.br
Feel free to use this code, hope it helps you in some way

### Related
Checkout Ikebana Front End application using React:
[Ikebana Sanguetsu](https://github.com/fabricio7p/Ikebana-App-Frontend)
