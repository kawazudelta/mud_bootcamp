# Phase 4: Deployment Automation Deep Dive

This phase explains the logic inside `scripts/deploy.sh` which we created in the previous step. Understanding this script is key to troubleshooting "Teacher, my code isn't updating!" issues.

## The Script: `scripts/deploy.sh`

### Step 1: `git reset --hard origin/deploy`
**What it does:** It forces the server's local git repository to match the `deploy` branch on GitHub exactly.
**Why:** This destroys any "hotfixes" or manual changes you made on the server. This is intentional. **Production code should always come from the repo.** If you manually edited a file on the server to fix a bug, this step will wipe it out. Fix the bug in your local repo and push it!

### Step 2: `pip install -r requirements.prod.txt`
**What it does:** Checks if you added new libraries (like a new combat system plugin).
**Why:** Evennia won't start if a Python library is missing. We use `requirements.prod.txt` (which we created in Phase 2) to ensure `psycopg2` (database) and `service_identity` (SSL) are present.

### Step 3: `evennia migrate`
**What it does:** Updates the database schema (tables/columns).
**Why:** If you added a new field `is_undead` to your `Character` typeclass, Django needs to add that column to PostgreSQL. If this step fails, the deployment stops.

### Step 4: `evennia collectstatic`
**What it does:** Copies CSS/JS/Images from your game folder to the web serving directory.
**Why:** If you upload a new logo but forget this, the website will still show the old logo.

### Step 5: `sudo systemctl restart evennia`
**What it does:** Restarts the Python processes.
**Why:** Python loads code into memory on startup. It does not "see" your changed files until you restart.
**Safety:** We use `restart` (Full Shutdown -> Start) rather than `reload`.
*   *Reload* is faster but can leave "stale" objects in memory if you changed core logic.
*   *Restart* kicks players off for 5-10 seconds but guarantees a clean slate.

## Troubleshooting

### "Permission Denied" on Restart
If the script fails at Step 5 with a password prompt, you forgot the Sudoers setup.
**Fix:**
Run `sudo visudo -f /etc/sudoers.d/evennia-deploy` and ensure it contains:
```text
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart evennia
```

### "Database Locked" or "Migration Failed"
If `evennia migrate` fails, it usually means your local database and production database have drifted too far apart.
**Fix:** Check the logs `mymud/server/logs/server.log`. You may need to manually SSH in and troubleshoot the specific migration error.
