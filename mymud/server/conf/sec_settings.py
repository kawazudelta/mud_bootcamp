import os
import sys
from pathlib import Path

# 1. Load the .env file
# We look for .env in the repo root (../../..)
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'

if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Strip quotes if present
                if (value.startswith("'") and value.endswith("'")) or \
                   (value.startswith('"') and value.endswith('"')):
                    value = value[1:-1]
                os.environ[key] = value
else:
    print(f"WARNING: .env file not found at {env_path}")

# 2. Configure Django/Evennia from Environment
from django.core.exceptions import ImproperlyConfigured

def get_env(key, default=None):
    val = os.environ.get(key, default)
    if val is None:
        raise ImproperlyConfigured(f"Missing env var: {key}")
    return val

DEBUG = get_env('DEBUG', 'False') == 'True'
SECRET_KEY = get_env('DJANGO_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env('DB_NAME'),
        'USER': get_env('DB_USER'),
        'PASSWORD': get_env('DB_PASSWORD'),
        'HOST': get_env('DB_HOST'),
        'PORT': get_env('DB_PORT', '5432'),
    }
}

ALLOWED_HOSTS = [get_env('GAME_DOMAIN'), '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = [f"https://{get_env('GAME_DOMAIN')}"]

# Email
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = get_env('EMAIL_HOST')
    EMAIL_HOST_USER = get_env('EMAIL_USER', '')
    EMAIL_HOST_PASSWORD = get_env('EMAIL_PASSWORD', '')