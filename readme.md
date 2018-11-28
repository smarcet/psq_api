cd psq_api

virtualenv -p python3 .env

source .env/bin/activate

# Install reqs

pip install -r requirements.txt 

pip freeze > requirements.txt

pip install gunicorn psycopg2-binary

python manage.py makemigrations

python manage.py migrate

python manage.py migrate django_cron


https://docs.djangoproject.com/en/2.0/topics/migrations/

# create super user

python manage.py createsuperuser

# cron jobs

http://django-cron.readthedocs.io/en/latest/installation.html

python manage.py runcrons --force

# static files
python manage.py  collectstatic

# locale

django-admin makemessages -l es
django-admin compilemessages

# kill debug process

sudo lsof -t -i tcp:8000 | xargs kill -9

# postgre SQL

https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04

sudo -u postgres psql

\l  -- list databases.
\du -- list users

CREATE DATABASE psq;

GRANT ALL PRIVILEGES ON DATABASE psq TO psq_user;