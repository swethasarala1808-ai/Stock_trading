# Stock Trading App for Frappe/ERPNext

A complete stock portfolio and trading management app built on the Frappe framework.

## Features

- **Stock Portfolio** — Track multiple portfolios with live P&L calculations
- **Stock Trade** — Record Buy/Sell trades; auto-updates portfolio holdings on execution
- **Market Watchlist** — Watch stocks with alert price support and live quote refresh
- **Stock Settings** — Configure market data provider (Alpha Vantage, Mock, etc.)
- **Live Stock Dashboard** — Web page at `/stock_dashboard` with portfolio summary + live quotes
- **Scheduled Tasks** — Hourly portfolio value updates, daily watchlist refresh
- **REST API** — Whitelisted endpoints for quotes, trades, portfolio data

## DocTypes

| DocType | Description |
|---|---|
| Stock Portfolio | Main portfolio document with holdings child table |
| Stock Portfolio Holding | Child table: per-symbol position data |
| Stock Trade | Individual buy/sell trade record |
| Market Watchlist | Watchlist of symbols to monitor |
| Watchlist Stock Item | Child table for watchlist entries |
| Stock Settings | Single doctype for app-wide config |

## Install

### From GitHub (after pushing)

```bash
cd ~/frappe-bench
bash apps/stock_app/install_on_server.sh beauty.localhost
```

### Manual steps

```bash
cd ~/frappe-bench/apps
git clone https://github.com/swethasarala1808-ai/Stock_trading.git stock_app
echo "stock_app" >> ~/frappe-bench/sites/apps.txt
cd ~/frappe-bench
./env/bin/pip install -e apps/stock_app
bench --site beauty.localhost install-app stock_app
bench --site beauty.localhost migrate
bench --site beauty.localhost execute stock_app.install.after_install
```

## API Endpoints

All endpoints are accessible via `frappe.call()` or REST:

| Method | Description |
|---|---|
| `stock_app.api.stock_api.get_stock_quote` | Live quote for a symbol |
| `stock_app.api.stock_api.get_portfolio_summary` | Portfolio list for current user |
| `stock_app.api.stock_api.get_portfolio_holdings` | Detailed holdings for a portfolio |
| `stock_app.api.stock_api.get_recent_trades` | Recent trades for current user |
| `stock_app.api.stock_api.place_trade` | Create a new trade |
| `stock_app.api.stock_api.get_watchlist_quotes` | Quotes for all stocks in a watchlist |
| `stock_app.api.stock_api.get_dashboard_data` | Aggregated dashboard data |

## Market Data

By default, **Mock (Testing)** mode is used which returns realistic randomised prices for Indian stocks (RELIANCE, TCS, HDFCBANK, etc.).

To use real data, set your provider and API key in **Stock Settings** on the Frappe desk.

## Dashboard URL

After install, visit: `https://your-site/stock_dashboard`
