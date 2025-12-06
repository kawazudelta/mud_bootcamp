#!/bin/bash
set -e  # Exit on any error

# -----------------------------------------------------------------------------
# Evennia Production Deployment Script
# -----------------------------------------------------------------------------
# This script is designed to be run on the production server (Ubuntu).
# It assumes:
# 1. The repo is cloned to ~/mud_bootcamp
# 2. A virtual environment exists at ~/mud_bootcamp/venv
# 3. A .env file exists at ~/mud_bootcamp/.env with production secrets
# -----------------------------------------------------------------------------

PROJECT_DIR="$HOME/mud_bootcamp"
VENV_DIR="$PROJECT_DIR/venv"
GAME_DIR="$PROJECT_DIR/mymud"

echo "========================================================"
echo "Starting Deployment: $(date)"
echo "========================================================"

# 1. Navigate to Project Root
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory $PROJECT_DIR not found."
    exit 1
fi
cd "$PROJECT_DIR"

# 2. Pull Latest Code
echo ">>> Pulling latest code..."
git fetch origin deploy
git reset --hard origin/deploy

# 3. Update Python Dependencies
echo ">>> Updating dependencies..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.prod.txt

# 4. Evennia Management Tasks
echo ">>> Running Evennia management tasks..."
cd "$GAME_DIR"

# Database Migrations
echo "   - Applying migrations..."
evennia migrate

# Static Files (CSS/JS)
echo "   - Collecting static files..."
evennia collectstatic --noinput

# 5. Restart Service
echo ">>> Restarting Evennia service..."
if systemctl is-active --quiet evennia; then
    sudo systemctl restart evennia
    echo "   - Service restarted."
else
    echo "   - Service 'evennia' is not running or not installed."
    echo "   - Attempting to start..."
    sudo systemctl start evennia || echo "Warning: Could not start service. Check logs."
fi

echo "========================================================"
echo "Deployment Complete!"
echo "========================================================"
