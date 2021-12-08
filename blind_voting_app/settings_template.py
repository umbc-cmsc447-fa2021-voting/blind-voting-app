# THIS IS A SETTINGS TEMPLATE FOR TESTING PURPOSES, DO NOT USE IN PRODUCTION

# This value is used for securing signed data, DO NOT EXPOSE YOUR VERSION OF THIS TO GIT.

SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

ALLOWED_HOSTS = []

DEFAULT_DOMAIN = 'http://localhost:8000'

# Django email backend to use
# https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-EMAIL_BACKEND

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database(s) configuration
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

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