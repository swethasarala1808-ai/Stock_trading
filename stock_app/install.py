import frappe


def after_install():
    """Run after app is installed on a site."""
    print("Stock App: Running after_install...")
    _create_default_settings()
    _create_roles()
    _create_default_watchlist()
    frappe.db.commit()
    print("Stock App: Installation complete!")


def after_migrate():
    """Run after each bench migrate."""
    print("Stock App: Running after_migrate...")
    _create_default_settings()
    frappe.db.commit()
    print("Stock App: Migration hooks done.")


def _create_default_settings():
    """Create or update default Stock Settings."""
    if not frappe.db.exists("Stock Settings", "Stock Settings"):
        doc = frappe.new_doc("Stock Settings")
        doc.default_currency = "INR"
        doc.market_data_provider = "Alpha Vantage"
        doc.api_key = ""
        doc.enable_auto_refresh = 0
        doc.refresh_interval_minutes = 15
        doc.insert(ignore_permissions=True)
        print("Stock App: Default Stock Settings created.")
    else:
        print("Stock App: Stock Settings already exist.")


def _create_roles():
    """Create custom roles for the stock app."""
    roles = ["Stock Trader", "Portfolio Manager", "Market Analyst"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.desk_access = 1
            role.insert(ignore_permissions=True)
            print(f"Stock App: Role '{role_name}' created.")


def _create_default_watchlist():
    """Create a sample default watchlist."""
    if not frappe.db.exists("Market Watchlist", "Default Watchlist"):
        doc = frappe.new_doc("Market Watchlist")
        doc.watchlist_name = "Default Watchlist"
        doc.description = "Default market watchlist with popular Indian stocks"
        doc.is_active = 1
        doc.insert(ignore_permissions=True)
        print("Stock App: Default watchlist created.")
