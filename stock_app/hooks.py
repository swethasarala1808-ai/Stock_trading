app_name = "stock_app"
app_title = "Stock Trading App"
app_publisher = "Stock App"
app_description = "A complete stock trading and portfolio management app for Frappe/ERPNext"
app_email = "admin@example.com"
app_license = "MIT"
app_version = "1.0.0"

# --------------------------------------------------------------------------
# Installation hooks
# --------------------------------------------------------------------------
after_install = "stock_app.install.after_install"
after_migrate = "stock_app.install.after_migrate"

# --------------------------------------------------------------------------
# Website routes
# --------------------------------------------------------------------------
website_route_rules = [
    {"from_route": "/stock_dashboard", "to_route": "stock_dashboard"},
    {"from_route": "/stock_dashboard/<path:name>", "to_route": "stock_dashboard"},
]

# --------------------------------------------------------------------------
# Scheduled tasks
# --------------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "stock_app.tasks.daily.refresh_market_data",
    ],
    "hourly": [
        "stock_app.tasks.hourly.update_portfolio_values",
    ],
}

# --------------------------------------------------------------------------
# Permissions
# --------------------------------------------------------------------------
has_permission = {
    "Stock Trade": "stock_app.permissions.has_permission",
}

# --------------------------------------------------------------------------
# DocType JS files
# --------------------------------------------------------------------------
doctype_js = {
    "Stock Trade": "public/js/stock_trade.js",
    "Stock Portfolio": "public/js/stock_portfolio.js",
    "Market Watchlist": "public/js/market_watchlist.js",
}

# --------------------------------------------------------------------------
# Whitelisted API methods
# --------------------------------------------------------------------------
# All methods decorated with @frappe.whitelist() are auto-discovered
