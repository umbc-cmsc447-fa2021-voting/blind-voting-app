# Blind Voting App
Repository for the Blind Voting Application. Built with Django!  

## Requirements  
python v3.9.1 or compatible  
pip v21.3 or compatible  
postgreSQL v14.0 w/ pgAdmin v4.0 or compatible
django-cryptography v1.0 or compatible

## Virtual Environment Setup
Follow the following steps to set yourself up for developing blind-voting-app:
```shell  
python -m venv .venv                        # Setup your virtual environment
python -m venv ./.venv/Scripts/activate     # Activate your new virutal environment
python -m pip install -r requirements.txt   # Install requirements listen in requirements.txt
```  

## Django configuration
It is necessary to create a personal django settings file which includes some configuration data not available in `blind_voting_app/settings_shared.py`. For testing convience, a template settings file has been included at `blind_voting_app/settings_template.py`. The naming convention for personal settings files is `settings_development.py`.

## Databse Setup  
With Django's ORM and migration capabilities, the webapp may be possible to operate using alternative database systems, however we officially support PostgreSQL. After creating your database (which we recommend doing through pgAdmin), place the following python code in your `blind_voting_app/settings_development.py` file with the correct information filled in:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database_name_here',
        'USER': 'username_here',
        'PASSWORD': 'password_here',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```  
If you would like to use SQLite3, please place the following python code in your development settings:
```python
BASE_DB_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DB_DIR / 'db.sqlite3',
    }
}
```
Test a successful connection by running the following command:
```shell
python manage.py migrate
```
Afterwards, verify that the table data has been properly created in your database.

## Run Web Server
To launch the web app run
```shell
python manage.py runserver
```
and visit the url indicated in the console! Enjoy!

## Using the Application
Please refer to the READMEs of the various application folders (/users and /ballots) for tips on operating the application.

## Testing
To run the Django test suite, issue the command:  
```shell
python manage.py test
```
If you experience an error that reads something like "Missing staticfiles manifest entry for '...'," run the command
```shell
python manage.py collectstatic
```

## Contributing  
Be sure to save any new dependencies installed through pip by issuing the command:  
```shell  
python -m pip freeze > requirements.txt
```  
