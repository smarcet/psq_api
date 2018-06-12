cd psq_api
virtualenv -p python3 .env
source .env/bin/activate

# Install reqs
pip install -r requirements.txt 

pip freeze > requirements.txt

manage.py makemigrations
manage.py migrate
manage.py migrate django_cron

https://docs.djangoproject.com/en/2.0/topics/migrations/

# create super user

manage.py createsuperuser

# cron jobs

http://django-cron.readthedocs.io/en/latest/installation.html

python manage.py runcrons --force

# locale

django-admin makemessages -l es
django-admin compilemessages
