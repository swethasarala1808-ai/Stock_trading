#!/bin/bash
# ══════════════════════════════════════════════════════════════════
# stock_deploy.sh  — Deploy Stock App v3 (Bizaxl Full Platform)
# Run from: ~/frappe-bench
# Usage:    bash stock_deploy.sh
# Safe:     Only touches stock_app on beauty.localhost
#           Does NOT affect any other site or app
# ══════════════════════════════════════════════════════════════════
set -e

BENCH="$HOME/frappe-bench"
APPS="$BENCH/apps"
SITE="beauty.localhost"
PIP="$BENCH/env/bin/pip"
PY="$BENCH/env/bin/python"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Bizaxl Stock App v3 — Full Platform Deploy"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── 1. Find the zip ───────────────────────────────────────────
ZIP=""
for f in "$HOME/stock_v3.zip" "$HOME/Downloads/stock_v3.zip" "/tmp/stock_v3.zip" "$BENCH/stock_v3.zip"; do
  [ -f "$f" ] && ZIP="$f" && break
done
if [ -z "$ZIP" ]; then
  echo "❌ Cannot find stock_v3.zip. Copy it first:"
  echo "   cp /mnt/c/Users/Swetha/Downloads/stock_v3.zip ~/stock_v3.zip"
  exit 1
fi
echo "▶ Found zip: $ZIP"

# ── 2. Uninstall old stock_app safely ─────────────────────────
echo "▶ Uninstalling old stock_app from $SITE..."
cd "$BENCH"
bench --site "$SITE" uninstall-app stock_app --yes 2>/dev/null \
  && echo "   ✅ Uninstalled" || echo "   (not installed, continuing)"

$PIP uninstall stock_app -y 2>/dev/null || true
echo "   ✅ pip uninstalled"

# ── 3. Remove old app folder ──────────────────────────────────
echo "▶ Removing old stock_app folder..."
rm -rf "$APPS/stock_app"
rm -rf "$APPS/stock_app_v2" 2>/dev/null || true
echo "   ✅ Removed"

# ── 4. Extract zip → apps/stock_v3, then rename to stock_app ──
echo "▶ Extracting stock_v3.zip..."
cd "$APPS"
unzip -o "$ZIP" -d ./ > /dev/null
# zip extracts to stock_v3/ folder
if [ -d "$APPS/stock_v3" ]; then
  mv "$APPS/stock_v3" "$APPS/stock_app"
  echo "   ✅ Extracted to apps/stock_app"
else
  echo "   ❌ Extraction failed — stock_v3 folder not found"
  ls "$APPS/"
  exit 1
fi

# ── 5. Verify setup.py exists ─────────────────────────────────
echo "▶ Verifying structure..."
[ -f "$APPS/stock_app/setup.py" ] && echo "   ✅ setup.py found" || { echo "   ❌ setup.py MISSING"; exit 1; }
[ -f "$APPS/stock_app/stock_app/modules.txt" ] && echo "   ✅ modules.txt: $(cat $APPS/stock_app/stock_app/modules.txt)" || { echo "   ❌ modules.txt MISSING"; exit 1; }
[ -f "$APPS/stock_app/stock_app/www/stock-dashboard.html" ] && echo "   ✅ stock-dashboard.html found" || echo "   ⚠️  stock-dashboard.html missing"
[ -f "$APPS/stock_app/stock_app/www/stock.html" ] && echo "   ✅ stock.html found" || echo "   ⚠️  stock.html missing"

# ── 6. Verify find_packages is clean ──────────────────────────
echo "▶ Verifying Python packages..."
cd "$APPS/stock_app"
$PY -c "
from setuptools import find_packages
pkgs = find_packages()
bad = [p for p in pkgs if any(c in p for c in ['{','}','\"'])]
if bad:
    print('❌ Bad packages found:', bad)
    exit(1)
print(f'   ✅ {len(pkgs)} clean packages found')
"

# ── 7. pip install ────────────────────────────────────────────
echo "▶ pip install -e apps/stock_app..."
cd "$BENCH"
$PIP install -e apps/stock_app -q
echo "   ✅ pip install done"

# ── 8. Verify Python imports ──────────────────────────────────
echo "▶ Verifying imports..."
$PY -c "
import stock_app, stock_app.hooks, stock_app.install
import stock_app.stock, stock_app.api
print('   ✅ All imports OK:', stock_app.__file__)
"

# ── 9. Register in apps.txt ───────────────────────────────────
echo "▶ Registering in sites/apps.txt..."
grep -qx "stock_app" "$BENCH/sites/apps.txt" 2>/dev/null \
  || echo "stock_app" >> "$BENCH/sites/apps.txt"
echo "   ✅ Registered"

# ── 10. Install app on site ───────────────────────────────────
echo "▶ bench install-app stock_app on $SITE..."
bench --site "$SITE" install-app stock_app
echo "   ✅ App installed"

# ── 11. Migrate ───────────────────────────────────────────────
echo "▶ bench migrate $SITE..."
bench --site "$SITE" migrate
echo "   ✅ Migration done"

# ── 12. Run after_migrate (sample data) ──────────────────────
echo "▶ Running after_migrate to create sample data..."
bench --site "$SITE" execute stock_app.install.after_migrate
echo "   ✅ Sample data created"

# ── 13. Clear caches ─────────────────────────────────────────
echo "▶ Clearing caches..."
bench --site "$SITE" clear-cache 2>/dev/null || true
bench --site "$SITE" clear-website-cache 2>/dev/null || true
echo "   ✅ Caches cleared"

# ── 14. Restart bench ────────────────────────────────────────
echo "▶ Restarting bench..."
bench restart 2>/dev/null || supervisorctl restart all 2>/dev/null || true
echo "   ✅ Restarted"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ DEPLOY COMPLETE!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Customer Portal:  http://beauty.localhost/stock"
echo "  Owner Dashboard:  http://beauty.localhost/stock-dashboard"
echo "  Frappe Desk:      http://beauty.localhost/app"
echo ""
echo "  Modules in desk:  Search 'Stock' in app list"
echo "  27 DocTypes:      Stock Client, Stock Order, Stock KYC..."
echo ""
