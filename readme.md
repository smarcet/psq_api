virtualenv -p python3 .env
pip install

pip freeze > requirements.txt

manage.py makemigrations
manage.py migrate

https://docs.djangoproject.com/en/2.0/topics/migrations/