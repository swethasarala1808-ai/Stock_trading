import frappe


def update_portfolio_values():
    """Hourly task: update portfolio current values based on latest prices."""
    frappe.logger().info("Stock App: Running hourly portfolio value update...")

    portfolios = frappe.get_all("Stock Portfolio", fields=["name"])

    for p in portfolios:
        try:
            doc = frappe.get_doc("Stock Portfolio", p.name)
            from stock_app.api.stock_api import get_stock_quote

            for holding in doc.holdings or []:
                try:
                    quote = get_stock_quote(holding.symbol)
                    current_price = quote.get("price", holding.current_price)
                    holding.current_price = current_price
                    holding.current_value = holding.quantity * current_price
                    holding.profit_loss = holding.current_value - (holding.total_invested or 0)
                    holding.profit_loss_percent = (
                        (holding.profit_loss / holding.total_invested * 100)
                        if holding.total_invested
                        else 0
                    )
                except Exception as e:
                    frappe.log_error(str(e), f"Price update failed for {holding.symbol}")

            doc.calculate_totals()
            doc.save(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(str(e), f"Portfolio update failed: {p.name}")

    frappe.db.commit()
    frappe.logger().info("Stock App: Hourly portfolio value update complete.")
