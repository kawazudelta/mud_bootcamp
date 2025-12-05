import secrets
import string

def generate_secret_key(length=50):
    """Generates a secure random string for DJANGO_SECRET_KEY."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+")"
    return ''.join(secrets.choice(chars) for i in range(length))

def generate_db_password(length=20):
    """Generates a secure alphanumeric password for DB."""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for i in range(length))

template = f"""# .env - Production Environment Variables
# COPY THIS FILE TO: /home/ubuntu/mud_bootcamp/.env
# CHANGE PERMISSIONS: chmod 600 .env

# --- Database (AWS RDS) ---
DB_NAME='mymud_db'
DB_USER='mymud_admin'
DB_PASSWORD='{generate_db_password()}'
DB_HOST='fill-in-your-rds-endpoint.us-east-1.rds.amazonaws.com'
DB_PORT='5432'

# --- Security ---
DJANGO_SECRET_KEY='{generate_secret_key()}'
DEBUG='False'

# --- Networking ---
# The domain name or IP players use to connect
GAME_DOMAIN='mymud.example.com'

# --- Email (Optional) ---
# EMAIL_USER='apikey'
# EMAIL_PASSWORD='...' """

if __name__ == "__main__":
    print(template)
    print("\n# >>> INSTRUCTIONS <<<")
    print("# 1. Run: python3 scripts/generate_env.py > .env_template")
    print("# 2. Edit .env_template to add your real AWS RDS Hostname.")
    print("# 3. Upload to server: scp .env_template ubuntu@<ip>:mud_bootcamp/.env")
