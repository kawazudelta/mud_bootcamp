# Phase 5: Security Best Practices

## 1. Nginx Reverse Proxy (SSL Termination)
Never expose Evennia's web server (port 4001) directly to the internet in production. It is not designed to handle DDoS or strict SSL/TLS ciphers.

**Configuration:**
Install Nginx: `sudo apt install nginx certbot python3-certbot-nginx`

**File:** `/etc/nginx/sites-available/mymud`
```nginx
server {
    server_name mymud.example.com;

    # Serve Static Files directly via Nginx (Faster than Django)
    location /static/ {
        alias /home/ubuntu/mud_bootcamp/mymud/web/static/;
        expires 30d;
        access_log off;
    }

    # Proxy Web Traffic
    location / {
        proxy_pass http://127.0.0.1:4001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy WebSocket Traffic (Crucial for WebClient)
    location /ws {
        proxy_pass http://127.0.0.1:4002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Enable it: `sudo ln -s /etc/nginx/sites-available/mymud /etc/nginx/sites-enabled/`
Secure it: `sudo certbot --nginx -d mymud.example.com`

## 2. Django Security Settings (Explained)
In Phase 2, we added specific settings to `secret_settings.py`. Here is why they are critical:

*   **`CSRF_TRUSTED_ORIGINS = ['https://mymud.example.com']`**
    *   *The Risk:* Django blocks "Cross Site Request Forgery" attacks. It checks the `Origin` header of a POST request (like a login) against the host it thinks it's running on.
    *   *The Fix:* Since Nginx sits in front, Django sees the request coming from `localhost` but the browser says it's from `mymud.example.com`. This setting tells Django "It's okay, we trust that domain." **Without this, you cannot log in to the admin panel.**
*   **`SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`**
    *   *The Fix:* Tells Django "If Nginx says this request was HTTPS, treat it as secure," allowing it to set secure cookies.

## 3. Firewall Hardening (UFW)
On Ubuntu, use `ufw` (Uncomplicated Firewall).
```bash
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 80/tcp   # For Certbot challenge
sudo ufw allow 443/tcp  # For Secure Web
sudo ufw allow 4000/tcp # Telnet (Legacy MUD clients)
# Note: We do NOT allow 4001 or 4002 externally. Only Nginx talks to them locally.
sudo ufw enable
```

## 4. SSH Hardening
Edit `/etc/ssh/sshd_config`:
*   `PasswordAuthentication no` (Force Key-based auth)
*   `PermitRootLogin no`
*   `MaxAuthTries 3`

## 5. Backups
AWS Lightsail has "Automatic Snapshots". **Enable them.** It costs pennies and saves your entire server state.
Additionally, setup a cron job to dump the Postgres DB to S3 nightly using `pg_dump` + `aws s3 cp`.
