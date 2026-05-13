import frappe


def has_permission(doc, ptype="read", user=None):
    """Custom permission handler for Stock Trade doctype."""
    user = user or frappe.session.user

    # Administrators and System Managers can do anything
    if frappe.has_role("System Manager", user) or frappe.has_role("Administrator", user):
        return True

    # Portfolio Managers can read all trades
    if ptype == "read" and frappe.has_role("Portfolio Manager", user):
        return True

    # Stock Traders can only access their own trades
    if doc and doc.trader == user:
        return True

    return False
