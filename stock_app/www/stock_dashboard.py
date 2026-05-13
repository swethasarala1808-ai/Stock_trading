import frappe


def get_context(context):
    """Prepare context for the stock dashboard www page."""
    if frappe.session.user == "Guest":
        frappe.throw(
            "You must be logged in to access the Stock Dashboard.",
            frappe.PermissionError,
        )

    context.no_cache = 1
    context.show_sidebar = False
    context.title = "Stock Dashboard"

    user = frappe.session.user
    context.user_fullname = frappe.db.get_value("User", user, "full_name") or user

    portfolios = frappe.get_all(
        "Stock Portfolio",
        filters={"trader": user},
        fields=["name", "portfolio_name", "total_invested",
                "current_value", "profit_loss", "profit_loss_percent"],
    )

    total_invested = sum(p.get("total_invested") or 0 for p in portfolios)
    current_value = sum(p.get("current_value") or 0 for p in portfolios)
    total_pl = current_value - total_invested
    total_pl_pct = (total_pl / total_invested * 100) if total_invested else 0

    context.summary = {
        "total_portfolios": len(portfolios),
        "total_invested": total_invested,
        "current_value": current_value,
        "total_profit_loss": total_pl,
        "total_profit_loss_percent": round(total_pl_pct, 2),
    }

    context.portfolios = portfolios

    context.recent_trades = frappe.get_all(
        "Stock Trade",
        filters={"trader": user},
        fields=["name", "trade_date", "trade_type", "symbol",
                "company_name", "quantity", "price_per_share",
                "net_amount", "status"],
        order_by="trade_date desc",
        limit=10,
    )

    context.watchlists = frappe.get_all(
        "Market Watchlist",
        filters={"is_active": 1},
        fields=["name", "watchlist_name"],
    )
