import frappe
from frappe.model.document import Document


class MarketWatchlist(Document):
    def validate(self):
        self.remove_duplicate_stocks()

    def remove_duplicate_stocks(self):
        seen = set()
        unique_stocks = []
        for row in self.stocks or []:
            if row.symbol not in seen:
                seen.add(row.symbol)
                unique_stocks.append(row)
        self.stocks = unique_stocks
