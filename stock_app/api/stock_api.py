import frappe
from frappe import _
import requests
import json


# ─────────────────────────────────────────────
# Portfolio APIs
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_portfolio_summary(portfolio_name=None):
    """Return portfolio summary for the current user."""
    user = frappe.session.user

    filters = {"trader": user}
    if portfolio_name:
        filters["name"] = portfolio_name

    portfolios = frappe.get_all(
        "Stock Portfolio",
        filters=filters,
        fields=["name", "portfolio_name", "total_invested", "current_value",
                "profit_loss", "profit_loss_percent"],
    )
    return portfolios


@frappe.whitelist()
def get_portfolio_holdings(portfolio_name):
    """Return detailed holdings for a specific portfolio."""
    if not frappe.db.exists("Stock Portfolio", portfolio_name):
        frappe.throw(_("Portfolio not found"), frappe.DoesNotExistError)

    doc = frappe.get_doc("Stock Portfolio", portfolio_name)

    return {
        "portfolio_name": doc.portfolio_name,
        "total_invested": doc.total_invested,
        "current_value": doc.current_value,
        "profit_loss": doc.profit_loss,
        "profit_loss_percent": doc.profit_loss_percent,
        "holdings": [
            {
                "symbol": h.symbol,
                "company_name": h.company_name,
                "quantity": h.quantity,
                "avg_buy_price": h.avg_buy_price,
                "total_invested": h.total_invested,
                "current_price": h.current_price,
                "current_value": h.current_value,
                "profit_loss": h.profit_loss,
                "profit_loss_percent": h.profit_loss_percent,
            }
            for h in doc.holdings or []
        ],
    }


# ─────────────────────────────────────────────
# Trade APIs
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_recent_trades(limit=20, portfolio_name=None):
    """Return recent trades for the current user."""
    user = frappe.session.user
    filters = {"trader": user}
    if portfolio_name:
        filters["portfolio"] = portfolio_name

    trades = frappe.get_all(
        "Stock Trade",
        filters=filters,
        fields=[
            "name", "trade_date", "trade_type", "symbol", "company_name",
            "quantity", "price_per_share", "net_amount", "status",
        ],
        order_by="trade_date desc",
        limit=int(limit),
    )
    return trades


@frappe.whitelist()
def place_trade(symbol, trade_type, quantity, price_per_share,
                portfolio_name=None, brokerage_fee=0, notes=""):
    """Place a new stock trade."""
    if trade_type not in ("Buy", "Sell"):
        frappe.throw(_("Invalid trade type. Must be 'Buy' or 'Sell'."))

    try:
        quantity = int(quantity)
        price_per_share = float(price_per_share)
        brokerage_fee = float(brokerage_fee)
    except (ValueError, TypeError):
        frappe.throw(_("Invalid numeric values provided."))

    if quantity <= 0:
        frappe.throw(_("Quantity must be greater than 0."))
    if price_per_share <= 0:
        frappe.throw(_("Price per share must be greater than 0."))

    trade = frappe.new_doc("Stock Trade")
    trade.trade_date = frappe.utils.today()
    trade.trade_type = trade_type
    trade.symbol = symbol.upper()
    trade.quantity = quantity
    trade.price_per_share = price_per_share
    trade.brokerage_fee = brokerage_fee
    trade.trader = frappe.session.user
    trade.notes = notes
    trade.status = "Pending"

    if portfolio_name:
        trade.portfolio = portfolio_name

    trade.insert(ignore_permissions=False)
    frappe.db.commit()

    return {"trade_id": trade.name, "status": "created"}


# ─────────────────────────────────────────────
# Market Data APIs
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_stock_quote(symbol):
    """Fetch live stock quote. Uses mock data if no API key configured."""
    symbol = symbol.upper()
    settings = frappe.get_single("Stock Settings")

    if settings.market_data_provider == "Mock (Testing)" or not settings.api_key:
        return _mock_quote(symbol)

    if settings.market_data_provider == "Alpha Vantage":
        return _alpha_vantage_quote(symbol, settings.api_key)

    return _mock_quote(symbol)


def _mock_quote(symbol):
    """Return realistic mock data for testing."""
    import random
    base_prices = {
        "RELIANCE": 2450.0, "TCS": 3800.0, "HDFCBANK": 1650.0,
        "INFY": 1450.0, "WIPRO": 420.0, "SBIN": 620.0,
        "ICICIBANK": 950.0, "KOTAKBANK": 1780.0, "BHARTIARTL": 870.0,
        "ITC": 440.0,
    }
    base = base_prices.get(symbol, 1000.0)
    price = round(base * (1 + random.uniform(-0.05, 0.05)), 2)
    change = round(price - base, 2)
    change_pct = round((change / base) * 100, 2)

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_percent": change_pct,
        "high": round(price * 1.02, 2),
        "low": round(price * 0.98, 2),
        "volume": random.randint(100000, 5000000),
        "source": "Mock Data",
    }


def _alpha_vantage_quote(symbol, api_key):
    """Fetch from Alpha Vantage API."""
    try:
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()
        quote = data.get("Global Quote", {})

        if not quote:
            return _mock_quote(symbol)

        price = float(quote.get("05. price", 0))
        change = float(quote.get("09. change", 0))
        change_pct = quote.get("10. change percent", "0%").replace("%", "")

        return {
            "symbol": symbol,
            "price": price,
            "change": change,
            "change_percent": float(change_pct),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "volume": int(quote.get("06. volume", 0)),
            "source": "Alpha Vantage",
        }
    except Exception as e:
        frappe.log_error(str(e), "Stock Quote Error")
        return _mock_quote(symbol)


@frappe.whitelist()
def get_watchlist_quotes(watchlist_name):
    """Fetch quotes for all stocks in a watchlist."""
    if not frappe.db.exists("Market Watchlist", watchlist_name):
        frappe.throw(_("Watchlist not found"))

    doc = frappe.get_doc("Market Watchlist", watchlist_name)
    quotes = []

    for stock in doc.stocks or []:
        quote = get_stock_quote(stock.symbol)
        quote["alert_price"] = stock.alert_price
        quotes.append(quote)

    return quotes


@frappe.whitelist()
def get_dashboard_data():
    """Return aggregated data for the stock dashboard page."""
    user = frappe.session.user

    portfolios = frappe.get_all(
        "Stock Portfolio",
        filters={"trader": user},
        fields=["name", "portfolio_name", "total_invested", "current_value",
                "profit_loss", "profit_loss_percent"],
    )

    total_invested = sum(p.get("total_invested") or 0 for p in portfolios)
    current_value = sum(p.get("current_value") or 0 for p in portfolios)
    total_pl = current_value - total_invested
    total_pl_pct = (total_pl / total_invested * 100) if total_invested else 0

    recent_trades = frappe.get_all(
        "Stock Trade",
        filters={"trader": user},
        fields=["name", "trade_date", "trade_type", "symbol",
                "quantity", "price_per_share", "status"],
        order_by="trade_date desc",
        limit=5,
    )

    watchlists = frappe.get_all(
        "Market Watchlist",
        filters={"is_active": 1},
        fields=["name", "watchlist_name"],
        limit=5,
    )

    return {
        "summary": {
            "total_portfolios": len(portfolios),
            "total_invested": total_invested,
            "current_value": current_value,
            "total_profit_loss": total_pl,
            "total_profit_loss_percent": round(total_pl_pct, 2),
        },
        "portfolios": portfolios,
        "recent_trades": recent_trades,
        "watchlists": watchlists,
    }
