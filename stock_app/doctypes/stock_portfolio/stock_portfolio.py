import frappe
from frappe.model.document import Document


class StockPortfolio(Document):
    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        total_invested = 0.0
        current_value = 0.0

        for row in self.holdings or []:
            total_invested += flt(row.total_invested)
            current_value += flt(row.current_value)

        self.total_invested = total_invested
        self.current_value = current_value
        self.profit_loss = current_value - total_invested
        self.profit_loss_percent = (
            (self.profit_loss / total_invested * 100) if total_invested else 0
        )

    def on_update(self):
        pass


def flt(val):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return 0.0
