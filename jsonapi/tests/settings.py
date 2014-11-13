# Settings to be used when running unit tests
# python manage.py test --settings=jsonapi.tests.settings jsonapi

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Pej^Ru}On@Id.oK,qUon?wuk:iV%yish&Vu+oJ.ret,vIb$hab'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    "jsonapi.tests",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
)

SITE_ID = 1

# This merely needs to be present - as long as your test case specifies a
# urls attribute, it does not need to be populated.
ROOT_URLCONF = 'jsonapi.tests.urls'

WSGI_APPLICATION = 'jsonapi.tests.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# For CI testing of releases
try:
    import django_jenkins
    CI = True
except:
    CI = False

if CI:
    INSTALLED_APPS += ('django_jenkins',)
    PROJECT_APPS = ('jsonapi.tests',)
    JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                     'django_jenkins.tasks.with_coverage')

