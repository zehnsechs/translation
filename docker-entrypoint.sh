#!/usr/bin/env bash

. /opt/translate/venv/bin/activate
cd /opt/translate/app

export DJANGO_SETTINGS_MODULE=Translation.settings
export LANG=C.UTF-8

ln -fs /usr/share/zoneinfo/${TRANS_TIME_ZONE:-UTC} /etc/localtime

dpkg-reconfigure --frontend noninteractive tzdata

fc-cache

if [[ -n $DB_HOST ]]; then
    while ! timeout 2 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/5432" 2> /dev/null; do
        echo "Waiting for db..."
        sleep 1
    done
fi

if [[ $# -eq 0 ]]; then
    echo "Collecting staticfiles"
    python3 manage.py collectstatic --noinput

    echo "Migrating Models"
    python3 manage.py migrate

    echo "Starting Gunicorn"

#	For using docker in development settings, add `--reload` option below to the execution line of gunicorn
    exec gunicorn Translation.wsgi:application -w "${GUNICORN_WORKERS:-1}" -b :9000
fi

exec "$@"
