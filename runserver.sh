#!/usr/bin/env sh

gunicorn -w 8 -t 360 main:app -b 0.0.0.0:5000
