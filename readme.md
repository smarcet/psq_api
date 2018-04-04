cd psq_api
virtualenv -p python3 .env
source .env/bin/activate

# Install reqs
pip install -r requirements.txt 

pip freeze > requirements.txt

manage.py makemigrations
manage.py migrate

https://docs.djangoproject.com/en/2.0/topics/migrations/