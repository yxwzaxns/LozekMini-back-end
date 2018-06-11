#!/usr/bin/env bash

export FLASK_DEBUG=1
export FLASK_APP=main.py
export FLASK_ENV=development

# gunicorn -w 2 --threads 2 --reload --access-logfile - --access-logformat "%(h)s%(l)s%(t)s %(r)s %(s)s"  -b 127.0.0.1:8000 main:app

gunicorn -w 1 --threads 1 --reload --access-logfile - --access-logformat "%(h)s%(l)s%(t)s %(r)s %(s)s"  -b 127.0.0.1:8000 main:app

# flask run -h 127.0.0.1 -p 8000
