# Phase 2: Configure the Application on Lightsail

## 1. Environment & Dependencies
We have created a dedicated requirements file for production to ensure stability.

*   **System Dependencies:**
    SSH into your Lightsail instance and run:
    ```bash
    sudo apt update && sudo apt install -y git python3-pip python3-venv libpq-dev
    ```

*   **Project Setup:**
    Clone your repository to the standard path we will use:
    ```bash
    git clone https://github.com/your/repo.git ~/mud_bootcamp
    ```

## 2. Configuration (The "12-Factor" Way)
We avoid hardcoding secrets. We have provided a script to help you generate the necessary configuration file.

**Step A: Generate the Environment File (Locally)**
Run the helper script included in the repo:
```bash
# From your local terminal in the repo root
python scripts/generate_env.py > production.env
```
*   Open `production.env` in a text editor.
*   **Fill in:** `DB_HOST` (Your RDS Endpoint).
*   **Fill in:** `GAME_DOMAIN` (Your Lightsail Static IP or Domain).

**Step B: Upload to Server**
Securely copy this file to the server.
```bash
scp production.env ubuntu@<your-lightsail-ip>:~/mud_bootcamp/.env
```

**Step C: Secure the File (On Server)**
```bash
# SSH into server
ssh ubuntu@<your-lightsail-ip>

# Restrict permissions so only the owner can read it
chmod 600 ~/mud_bootcamp/.env
```

## 3. Server-Side Setup
Now we configure the application to use this environment file.

**Create the Secret Settings Interface:**
We need to tell Evennia how to read that `.env` file. Create the following file on the server (or commit it to your repo if you prefer, as it contains no actual secrets):

**File:** `~/mud_bootcamp/mymud/server/conf/secret_settings.py`

```python
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
```

## 4. Initialization
Now that config is in place, initialize the database.

```bash
cd ~/mud_bootcamp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.prod.txt

cd mymud
evennia migrate
evennia collectstatic
```

## 5. Systemd Service
Create the service file to keep the game running.

**File:** `/etc/systemd/system/evennia.service`

```ini
[Unit]
Description=Evennia MUD Server
After=network.target postgresql.service

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/home/ubuntu/mud_bootcamp/mymud
# We load env vars in python, but this ensures PATH is correct
Environment="PATH=/home/ubuntu/mud_bootcamp/venv/bin:/usr/bin"
ExecStart=/home/ubuntu/mud_bootcamp/venv/bin/evennia start
ExecStop=/home/ubuntu/mud_bootcamp/venv/bin/evennia stop
PIDFile=/home/ubuntu/mud_bootcamp/mymud/server/server.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable it: `sudo systemctl enable evennia`
