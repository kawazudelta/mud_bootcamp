# Phase 1: Prepare AWS Infrastructure

## Pre-Flight Checklist
Before spinning up servers, ensure you have these items locally:
1.  **AWS Account:** You can log in to the AWS Console.
2.  **SSH Client:** You have `ssh` installed (Git Bash on Windows, or standard Terminal on Mac/Linux).
3.  **Key Pair Strategy:** You are ready to download a `.pem` file and keep it safe.

## 1. AWS Lightsail Instance (Compute)
Start with a single Lightsail VPS.
*   **OS:** Select **Ubuntu 24.04 LTS**.
    *   *Why?* Your project requires **Python 3.12**. Older Ubuntu versions (20.04/22.04) ship with older Python versions, requiring messy manual compilations. Ubuntu 24.04 includes Python 3.12 by default.
*   **Plan:** The $10-$12/mo plan (2GB RAM, 1 vCPU) is the **minimum recommended** for a production Evennia server. 512MB or 1GB plans *will* crash due to Out-Of-Memory errors during the `pip install` process.
*   **Networking:**
    *   Attach a **Static IP** immediately. This IP will be your `GAME_DOMAIN` later.
    *   **Firewall Rules (in Lightsail Console):**
        *   `SSH` (TCP 22): Restrict to your IP if possible.
        *   `Telnet` (TCP 4000): For MUD clients.
        *   `Web/HTTP` (TCP 4001): Evennia's web server (Temporary, until Nginx is up).
        *   `WebSocket` (TCP 4002): For the web client (Temporary).
        *   `HTTP` (TCP 80) & `HTTPS` (TCP 443): Add these now for Nginx later.

## 2. AWS RDS (PostgreSQL Database)
Managed databases save you from data loss.
*   **Create Database:** In the Lightsail Console, choose **Databases**.
*   **Engine:** PostgreSQL (Latest stable, e.g., 15+).
*   **Plan:** `db.t4g.micro` (Standard) or the High Availability option if budget permits.
*   **Credentials:** Write down the **Master Username** and **Master Password**. You will need these for the `generate_env.py` script.
*   **VPC Peering:**
    *   Go to **Account > Advanced > VPC Peering**.
    *   Check "Enable Peering" for your region (e.g., `us-east-1`).
    *   *Why?* Lightsail instances run in a "Shadow VPC". They cannot talk to other AWS services (like S3 or private RDS IPs) unless this is checked.

## 3. (Optional) S3 for Static Files
*   **Bucket:** Create a private S3 bucket (e.g., `mymud-static-assets`).
*   **User:** Create an IAM User with `Programmatic Access` and save the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
*   **Policy:** Grant `s3:PutObject` and `s3:GetObject` on that specific bucket.

## 4. Local Verification
Open your terminal and check your connection tools:
```bash
# Verify you can SSH (once instance is up)
ssh -i /path/to/your-key.pem ubuntu@<static-ip>

# Verify Python 3.12 is on the server
python3 --version
# Should say Python 3.12.x
```
