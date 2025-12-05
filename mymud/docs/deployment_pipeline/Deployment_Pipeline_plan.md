 # Deployment Pipeline Overview
  The project uses a standard 12-Factor App architecture hosted on AWS Lightsail. The server runs Ubuntu 24.04 (for Python 3.12 support) with a managed PostgreSQL  database (AWS RDS) and Nginx for SSL termination.

 ## 1. Phase 1: Infrastructure (Infra Engineer)
   * Compute: Provision an AWS Lightsail instance (Ubuntu 24.04, min. 2GB RAM).
   * Database: Create a managed PostgreSQL instance in AWS RDS (setup VPC peering).
   * Network: Attach a Static IP, configure Firewall (Open 80/443/4000; Close 4001/4002 externally), and setup DNS.
   * Hand-off: Provide the Static IP and RDS credentials to the App Developer.

  ## 2. Phase 2: Application Configuration (App Dev)
   * Environment: Generate production.env locally using scripts/generate_env.py and SCP it to the server (permissions 600).
   * Settings: Create secret_settings.py on the server to bridge .env vars to Evennia/Django.
   * Service: Install system dependencies, create the Python venv, and configure the evennia systemd service for auto-restart.

##  3. Phase 3: CI/CD Automation
   * Pipeline: A GitHub Actions workflow (deploy.yml) triggers on pushes to the deploy branch.
   * Execution: It connects via SSH and executes scripts/deploy.sh.
   * Secrets: Requires LIGHTSAIL_HOST, LIGHTSAIL_USERNAME, and LIGHTSAIL_SSH_KEY in GitHub Secrets.

 ## 4. Operations & Best Practices (Phases 4-6)
   * Automation: The deploy.sh script handles git reset (forcing exact repo match), pip install, DB migrations, and service restarts.
   * Security: Nginx handles SSL/TLS; firewall blocks direct access to internal ports; SSH is key-only.
   * Scaling: Vertical scaling (upgrading RAM/CPU) is the primary strategy. Static assets should be offloaded to S3/CDN if web traffic grows.