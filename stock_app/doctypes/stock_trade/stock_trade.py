import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


def flt(val):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return 0.0


class StockTrade(Document):
    def validate(self):
        self.calculate_amounts()
        self.set_trader()

    def set_trader(self):
        if not self.trader:
            self.trader = frappe.session.user

    def calculate_amounts(self):
        qty = flt(self.quantity)
        price = flt(self.price_per_share)
        fee = flt(self.brokerage_fee)

        self.total_amount = qty * price

        if self.trade_type == "Buy":
            self.net_amount = self.total_amount + fee
        else:
            self.net_amount = self.total_amount - fee

    def on_submit(self):
        self.status = "Executed"
        self.executed_at = now_datetime()
        self.update_portfolio()

    def on_cancel(self):
        self.status = "Cancelled"

    def update_portfolio(self):
        """Update the linked portfolio holdings after trade execution."""
        if not self.portfolio:
            return

        portfolio = frappe.get_doc("Stock Portfolio", self.portfolio)
        existing = None

        for holding in portfolio.holdings or []:
            if holding.symbol == self.symbol:
                existing = holding
                break

        if self.trade_type == "Buy":
            if existing:
                new_qty = flt(existing.quantity) + flt(self.quantity)
                new_invested = flt(existing.total_invested) + flt(self.net_amount)
                existing.quantity = new_qty
                existing.avg_buy_price = new_invested / new_qty if new_qty else 0
                existing.total_invested = new_invested
                existing.current_price = flt(self.price_per_share)
                existing.current_value = new_qty * flt(self.price_per_share)
                existing.profit_loss = existing.current_value - new_invested
                existing.profit_loss_percent = (
                    (existing.profit_loss / new_invested * 100) if new_invested else 0
                )
            else:
                portfolio.append("holdings", {
                    "symbol": self.symbol,
                    "company_name": self.company_name,
                    "quantity": flt(self.quantity),
                    "avg_buy_price": flt(self.price_per_share),
                    "total_invested": flt(self.net_amount),
                    "current_price": flt(self.price_per_share),
                    "current_value": flt(self.quantity) * flt(self.price_per_share),
                    "profit_loss": 0,
                    "profit_loss_percent": 0,
                })

        elif self.trade_type == "Sell" and existing:
            new_qty = flt(existing.quantity) - flt(self.quantity)
            if new_qty <= 0:
                portfolio.holdings.remove(existing)
            else:
                existing.quantity = new_qty
                existing.current_price = flt(self.price_per_share)
                existing.current_value = new_qty * flt(self.price_per_share)
                existing.profit_loss = existing.current_value - flt(existing.total_invested)
                existing.profit_loss_percent = (
                    (existing.profit_loss / flt(existing.total_invested) * 100)
                    if flt(existing.total_invested)
                    else 0
                )

        portfolio.calculate_totals()
        portfolio.save(ignore_permissions=True)
