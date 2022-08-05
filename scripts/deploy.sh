#!/bin/sh

set -e

python manage.py collectstatic --noinput
python /usr/src/manage.py makemigrations collector 
python /usr/src/manage.py migrate --noinput

uwsgi --socket :8000 --master --enable-threads --module collector.wsgi
