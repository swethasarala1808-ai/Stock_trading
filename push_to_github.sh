#!/bin/bash
# ─────────────────────────────────────────────────────────────
# push_to_github.sh
# Run this ONCE from ~/frappe-bench/apps/stock_app after cloning
# Usage: bash push_to_github.sh <YOUR_GITHUB_TOKEN>
# ─────────────────────────────────────────────────────────────

set -e

if [ -z "$1" ]; then
  echo "Usage: bash push_to_github.sh <YOUR_GITHUB_TOKEN>"
  exit 1
fi

TOKEN="$1"
REPO="https://${TOKEN}@github.com/swethasarala1808-ai/Stock_trading.git"

echo "Setting remote origin..."
git remote set-url origin "$REPO"

echo "Adding all files..."
git add -A

echo "Committing..."
git commit -m "Complete stock_app — all doctypes, API, www pages, install hooks" || echo "Nothing to commit."

echo "Pushing to main..."
git push origin main

echo ""
echo "✅ Push complete! Your code is now on GitHub."
echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Next steps — run on your Frappe server:"
echo ""
echo "  cd ~/frappe-bench/apps"
echo "  git clone https://\$TOKEN@github.com/swethasarala1808-ai/Stock_trading.git stock_app"
echo "  echo 'stock_app' >> ~/frappe-bench/sites/apps.txt"
echo "  cd ~/frappe-bench"
echo "  ./env/bin/pip install -e apps/stock_app"
echo "  bench --site beauty.localhost install-app stock_app"
echo "  bench --site beauty.localhost migrate"
echo "  bench --site beauty.localhost execute stock_app.install.after_install"
echo "─────────────────────────────────────────────────────────────"
