import frappe


def refresh_market_data():
    """Daily task: refresh market data for all active watchlists."""
    frappe.logger().info("Stock App: Running daily market data refresh...")

    watchlists = frappe.get_all(
        "Market Watchlist",
        filters={"is_active": 1},
        fields=["name"],
    )

    for wl in watchlists:
        try:
            doc = frappe.get_doc("Market Watchlist", wl.name)
            from stock_app.api.stock_api import get_stock_quote

            for stock in doc.stocks or []:
                try:
                    quote = get_stock_quote(stock.symbol)
                    stock.last_price = quote.get("price", stock.last_price)
                    stock.change_percent = quote.get("change_percent", stock.change_percent)
                except Exception as e:
                    frappe.log_error(str(e), f"Quote refresh failed for {stock.symbol}")

            doc.save(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(str(e), f"Watchlist refresh failed: {wl.name}")

    frappe.db.commit()
    frappe.logger().info("Stock App: Daily market data refresh complete.")
