# Deployment Architecture & Handoff Guide

This document serves as the "contract" between the Infrastructure Engineer (Phase 1) and the Application Developer (Phase 2+). It outlines the shared constants, paths, and architectural decisions that must not change without coordination.

## 1. The Architecture at a Glance
*   **Platform:** AWS Lightsail (Compute) + AWS RDS (Database) + S3 (Static Assets).
*   **OS:** Ubuntu 24.04 LTS (Critical for Python 3.12 support).
*   **Repo Strategy:** The server code is a direct mirror of the GitHub `deploy` branch.
*   **Secret Management:** 12-Factor App style. No secrets in code. All secrets live in a `.env` file on the server.

## 2. "Magic Values" (Do Not Deviate)
Both teams must agree on these constants. Changing them breaks the pipeline.

| Constant | Value | Why? |
| :--- | :--- | :--- |
| **Project Root** | `/home/ubuntu/mud_bootcamp` | Hardcoded in `deploy.sh` and `systemd` service. |
| **User** | `ubuntu` | Default Lightsail user. |
| **Python Ver** | `3.12` | Required by Evennia. Ubuntu 24.04 provides this natively. |
| **Database** | PostgreSQL (RDS) | `psycopg2` is in requirements. SQLite is disabled. |
| **Domain** | `GAME_DOMAIN` (Env Var) | Used for Allowed Hosts and CSRF trust. |

## 3. For the Infrastructure Engineer (Phase 1)
**What the App Dev needs you to get right:**
1.  **VPC Peering:** You *must* enable VPC Peering in Lightsail and configure the RDS Security Group to allow traffic from the Lightsail private IP. If you don't, the App Dev cannot connect to the DB.
2.  **Static IP:** Attach this immediately. The App Dev needs it to generate the `.env` file and set up DNS.
3.  **Ports:** Open `80/443` (Nginx), `22` (SSH), and `4000` (Telnet). Close `4001/4002` externally once Nginx is ready.

## 4. For the Application Developer (Phase 2)
**What the Infra Engineer assumes you know:**
1.  **No Local SQLite:** The prod config expects Postgres. You cannot run the prod settings without the RDS credentials.
2.  **The `.env` File:** The server will crash if `~/mud_bootcamp/.env` is missing. Use `scripts/generate_env.py` to build it locally, then `scp` it over.
3.  **Deployment:** Do not manually edit files on the server to fix bugs. The next deployment runs `git reset --hard` and will wipe your changes. Fix it in git, push to `deploy`, and run `scripts/deploy.sh`.

## 5. Shared Troubleshooting
*   **Logs:** `~/mud_bootcamp/mymud/server/logs/server.log`
*   **Service Status:** `sudo systemctl status evennia`
*   **Config Check:** Run `env` in the terminal to see if variables are loading (note: systemd env vars are separate, check `/etc/systemd/system/evennia.service` path).
