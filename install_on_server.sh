#!/bin/bash
# ─────────────────────────────────────────────────────────────
# install_on_server.sh
# Run this on your Frappe bench server after cloning from GitHub
# Usage: bash install_on_server.sh <SITE_NAME> [GITHUB_TOKEN]
#   e.g. bash install_on_server.sh beauty.localhost
# ─────────────────────────────────────────────────────────────

set -e

SITE="${1:-beauty.localhost}"
TOKEN="${2:-}"
BENCH_DIR="$HOME/frappe-bench"
APPS_DIR="$BENCH_DIR/apps"
REPO_URL="https://github.com/swethasarala1808-ai/Stock_trading.git"

echo "=== Stock App Server Installer ==="
echo "Site: $SITE"
echo "Bench: $BENCH_DIR"
echo ""

# Clone if not present
if [ ! -d "$APPS_DIR/stock_app" ]; then
  echo "Cloning stock_app from GitHub..."
  if [ -n "$TOKEN" ]; then
    git clone "https://${TOKEN}@github.com/swethasarala1808-ai/Stock_trading.git" "$APPS_DIR/stock_app"
  else
    git clone "$REPO_URL" "$APPS_DIR/stock_app"
  fi
else
  echo "stock_app already cloned. Pulling latest..."
  cd "$APPS_DIR/stock_app" && git pull origin main
fi

# Register app
if ! grep -q "stock_app" "$BENCH_DIR/sites/apps.txt" 2>/dev/null; then
  echo "Registering stock_app in apps.txt..."
  echo "stock_app" >> "$BENCH_DIR/sites/apps.txt"
fi

# pip install
echo "Installing Python package..."
cd "$BENCH_DIR"
./env/bin/pip install -e apps/stock_app

# Install on site
echo "Installing app on site $SITE..."
bench --site "$SITE" install-app stock_app

# Migrate
echo "Running migrations..."
bench --site "$SITE" migrate

# Run install hook
echo "Running after_install hook..."
bench --site "$SITE" execute stock_app.install.after_install

echo ""
echo "✅ stock_app installed successfully on $SITE!"
echo ""
echo "Visit your dashboard at: https://$SITE/stock_dashboard"
