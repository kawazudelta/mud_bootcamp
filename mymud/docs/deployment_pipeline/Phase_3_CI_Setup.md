# Phase 3: Continuous Integration Setup (GitHub Actions)

## Overview
We have standardized the deployment process using a script in the repository: `scripts/deploy.sh`. This ensures that what you run manually is exactly what the CI pipeline runs.

## 1. Setup GitHub Secrets
Go to your repository **Settings > Secrets and variables > Actions**. Add the following:

| Secret Name | Description |
| :--- | :--- |
| `LIGHTSAIL_HOST` | The **Public IP** of your Lightsail instance. |
| `LIGHTSAIL_USERNAME` | `ubuntu` |
| `LIGHTSAIL_SSH_KEY` | The contents of your `.pem` private key file. |
| `DISCORD_WEBHOOK` | (Optional) URL for deployment notifications. |

## 2. The CI Workflow
Create `.github/workflows/deploy.yml`.

```yaml
name: CI/CD

on:
  push:
    branches: [ "deploy" ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - name: Install Dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.prod.txt
      - name: Syntax Check
        run: |
          python -m compileall mymud/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Execute Deployment on Lightsail
        uses: appleboy/ssh-action@v0.1.8
        with:
          host: ${{ secrets.LIGHTSAIL_HOST }}
          username: ${{ secrets.LIGHTSAIL_USERNAME }}
          key: ${{ secrets.LIGHTSAIL_SSH_KEY }}
          script_stop: true
          # We simply execute the script we added to the repo
          script: |
            chmod +x ~/mud_bootcamp/scripts/deploy.sh
            ~/mud_bootcamp/scripts/deploy.sh
```

## 3. Why this is better
In the previous iteration, we embedded shell commands in the YAML. By moving them to `scripts/deploy.sh`, you gain:
1.  **Portability:** You can run `ssh ubuntu@<ip> ~/mud_bootcamp/scripts/deploy.sh` manually if GitHub is down.
2.  **Testability:** You can test the script on a staging server without committing to the repo.
3.  **Simplicity:** The CI config is tiny and unlikely to break.
