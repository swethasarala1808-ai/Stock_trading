import frappe
<<<<<<< HEAD
from frappe.utils import today, add_days, get_first_day


def after_install():
    print("Stock App: Running after_install...")
    _create_roles()
    frappe.db.commit()
    print("Stock App: after_install done. Run bench migrate then execute after_install again.")


def after_migrate():
    print("Stock App: Running after_migrate setup...")
    try:
        _create_settings()
        _create_relationship_managers()
        _create_brokerage_plans()
        _create_market_watch()
        _create_sample_clients()
        frappe.db.commit()
        print("Stock App: Setup complete!")
    except Exception as e:
        frappe.log_error(str(e), "after_migrate")
        print(f"Stock App: Setup error — {e}")


def _create_roles():
    for role in ["Stock Trader", "Stock Manager", "Stock Admin", "Stock RM"]:
        if not frappe.db.exists("Role", role):
            r = frappe.new_doc("Role")
            r.role_name = role
            r.desk_access = 1
            r.insert(ignore_permissions=True)
            print(f"  Role created: {role}")


def _create_settings():
    if not frappe.db.table_exists("tabStock Settings"):
        return
    doc = frappe.get_single("Stock Settings")
    doc.company_name = "Bizaxl Securities Pvt Ltd"
    doc.tagline = "Smart Brokerage & Wealth Management"
    doc.sebi_registration_number = "INZ000XXXXXX"
    doc.sebi_registration_type = "Stock Broker"
    doc.exchange_membership_nse = "NSE12345"
    doc.exchange_membership_bse = "BSE67890"
    doc.dp_name = "CDSL"
    doc.dp_id = "12345678"
    doc.gstin = "29XXXXXXXXXXXXX"
    doc.pan = "AAAAA0000A"
    doc.address = "123 Financial District, Hyderabad"
    doc.city = "Hyderabad"
    doc.state = "Telangana"
    doc.pincode = "500032"
    doc.phone = "040-12345678"
    doc.email = "support@bizaxl.com"
    doc.website = "https://bizaxl.com"
    doc.whatsapp_number = "9876543210"
    doc.monthly_statement_day = 1
    doc.margin_call_threshold_percent = 80
    doc.auto_square_off_threshold_percent = 90
    doc.save(ignore_permissions=True)
    print("  Stock Settings created")


def _create_relationship_managers():
    if not frappe.db.table_exists("tabStock Relationship Manager"):
        return
    rms = [
        {"rm_name": "Arjun Kumar", "email": "arjun@bizaxl.com", "phone": "9876543001",
         "employee_id": "EMP001", "designation": "Senior RM", "branch": "Hyderabad", "is_active": 1},
        {"rm_name": "Priya Sharma", "email": "priya@bizaxl.com", "phone": "9876543002",
         "employee_id": "EMP002", "designation": "Relationship Manager", "branch": "Mumbai", "is_active": 1},
        {"rm_name": "Ravi Nair", "email": "ravi@bizaxl.com", "phone": "9876543003",
         "employee_id": "EMP003", "designation": "Branch Manager", "branch": "Bangalore", "is_active": 1},
    ]
    for rm in rms:
        if not frappe.db.exists("Stock Relationship Manager", rm["rm_name"]):
            doc = frappe.new_doc("Stock Relationship Manager")
            for k, v in rm.items():
                setattr(doc, k, v)
            doc.insert(ignore_permissions=True)
            print(f"  RM created: {rm['rm_name']}")


def _create_brokerage_plans():
    if not frappe.db.table_exists("tabStock Brokerage Plan"):
        return
    plans = [
        {"plan_name": "Zero Brokerage", "plan_type": "Zero Brokerage",
         "description": "Zero brokerage on delivery, ₹20 flat on intraday",
         "equity_delivery_flat": 0, "equity_delivery_percent": 0,
         "equity_intraday_flat": 20, "equity_intraday_percent": 0.03,
         "futures_flat": 20, "options_per_lot": 20,
         "account_opening_charges": 0, "account_maintenance_annual": 300, "is_active": 1},
        {"plan_name": "Flat ₹20", "plan_type": "Flat Fee",
         "description": "₹20 flat across all segments",
         "equity_delivery_flat": 20, "equity_intraday_flat": 20,
         "futures_flat": 20, "options_per_lot": 20,
         "account_opening_charges": 500, "account_maintenance_annual": 300, "is_active": 1},
        {"plan_name": "Percentage Plan", "plan_type": "Percentage",
         "description": "0.5% delivery, 0.03% intraday",
         "equity_delivery_percent": 0.5, "equity_intraday_percent": 0.03,
         "futures_percent": 0.03, "options_percent": 0.03,
         "account_opening_charges": 0, "account_maintenance_annual": 0, "is_active": 1},
    ]
    for plan in plans:
        if not frappe.db.exists("Stock Brokerage Plan", plan["plan_name"]):
            doc = frappe.new_doc("Stock Brokerage Plan")
            for k, v in plan.items():
                setattr(doc, k, v)
            doc.insert(ignore_permissions=True)
            print(f"  Plan created: {plan['plan_name']}")


def _create_market_watch():
    if not frappe.db.table_exists("tabStock Market Watch"):
        return
    stocks = [
        {"symbol": "RELIANCE", "company_name": "Reliance Industries Ltd", "exchange": "NSE",
         "sector": "Energy", "last_price": 2847.50, "day_change": 23.40, "day_change_percent": 0.83,
         "fifty_two_week_high": 3024.90, "fifty_two_week_low": 2180.00, "volume": 8542310},
        {"symbol": "TCS", "company_name": "Tata Consultancy Services", "exchange": "NSE",
         "sector": "IT", "last_price": 3412.80, "day_change": -18.60, "day_change_percent": -0.54,
         "fifty_two_week_high": 4592.25, "fifty_two_week_low": 3056.05, "volume": 2134560},
        {"symbol": "INFY", "company_name": "Infosys Ltd", "exchange": "NSE",
         "sector": "IT", "last_price": 1456.30, "day_change": 12.80, "day_change_percent": 0.89,
         "fifty_two_week_high": 1953.90, "fifty_two_week_low": 1307.80, "volume": 5621890},
        {"symbol": "HDFCBANK", "company_name": "HDFC Bank Ltd", "exchange": "NSE",
         "sector": "Banking", "last_price": 1723.45, "day_change": -8.25, "day_change_percent": -0.48,
         "fifty_two_week_high": 1880.00, "fifty_two_week_low": 1363.55, "volume": 9876540},
        {"symbol": "ICICIBANK", "company_name": "ICICI Bank Ltd", "exchange": "NSE",
         "sector": "Banking", "last_price": 1187.60, "day_change": 15.40, "day_change_percent": 1.31,
         "fifty_two_week_high": 1196.65, "fifty_two_week_low": 854.70, "volume": 11234560},
        {"symbol": "WIPRO", "company_name": "Wipro Ltd", "exchange": "NSE",
         "sector": "IT", "last_price": 431.20, "day_change": -3.10, "day_change_percent": -0.71,
         "fifty_two_week_high": 569.70, "fifty_two_week_low": 373.75, "volume": 4532170},
        {"symbol": "SBIN", "company_name": "State Bank of India", "exchange": "NSE",
         "sector": "Banking", "last_price": 812.30, "day_change": 9.60, "day_change_percent": 1.20,
         "fifty_two_week_high": 912.00, "fifty_two_week_low": 543.15, "volume": 18765430},
        {"symbol": "BAJFINANCE", "company_name": "Bajaj Finance Ltd", "exchange": "NSE",
         "sector": "Banking", "last_price": 6834.50, "day_change": 45.20, "day_change_percent": 0.67,
         "fifty_two_week_high": 8192.00, "fifty_two_week_low": 5600.00, "volume": 1234560},
        {"symbol": "ASIANPAINT", "company_name": "Asian Paints Ltd", "exchange": "NSE",
         "sector": "FMCG", "last_price": 2234.70, "day_change": -12.30, "day_change_percent": -0.55,
         "fifty_two_week_high": 3217.25, "fifty_two_week_low": 2114.90, "volume": 876540},
        {"symbol": "MARUTI", "company_name": "Maruti Suzuki India Ltd", "exchange": "NSE",
         "sector": "Auto", "last_price": 11234.60, "day_change": 67.80, "day_change_percent": 0.61,
         "fifty_two_week_high": 13187.00, "fifty_two_week_low": 9832.40, "volume": 543210},
    ]
    for s in stocks:
        if not frappe.db.exists("Stock Market Watch", s["symbol"]):
            doc = frappe.new_doc("Stock Market Watch")
            for k, v in s.items():
                setattr(doc, k, v)
            doc.instrument_type = "Equity"
            doc.is_active = 1
            doc.insert(ignore_permissions=True)
    print(f"  Created {len(stocks)} market watch items")


def _create_sample_clients():
    if not frappe.db.table_exists("tabStock Client"):
        return

    clients_data = [
        {"full_name": "Rajesh Mehta", "phone": "9876501001", "email": "rajesh@email.com",
         "pan_number": "ABCPM1234A", "city": "Mumbai", "state": "Maharashtra",
         "client_type": "Individual", "risk_profile": "Aggressive",
         "account_status": "Account Active", "relationship_manager": "Arjun Kumar",
         "total_aum": 2500000, "portfolio_value": 2750000, "available_cash": 150000,
         "total_pnl": 250000, "trading_account_number": "TA001001", "demat_account_number": "1201750012345678"},
        {"full_name": "Priya Venkatesh", "phone": "9876501002", "email": "priya.v@email.com",
         "pan_number": "DEFPV5678B", "city": "Bangalore", "state": "Karnataka",
         "client_type": "Individual", "risk_profile": "Moderate",
         "account_status": "Account Active", "relationship_manager": "Priya Sharma",
         "total_aum": 1800000, "portfolio_value": 1920000, "available_cash": 80000,
         "total_pnl": 120000, "trading_account_number": "TA001002", "demat_account_number": "1201750023456789"},
        {"full_name": "Amit Gupta", "phone": "9876501003", "email": "amit.g@email.com",
         "pan_number": "GHIAG9012C", "city": "Delhi", "state": "Delhi",
         "client_type": "Individual", "risk_profile": "Conservative",
         "account_status": "Account Active", "relationship_manager": "Ravi Nair",
         "total_aum": 500000, "portfolio_value": 520000, "available_cash": 25000,
         "total_pnl": 20000},
        {"full_name": "Sunita Reddy", "phone": "9876501004", "email": "sunita.r@email.com",
         "pan_number": "JKLSR3456D", "city": "Hyderabad", "state": "Telangana",
         "client_type": "Individual", "risk_profile": "Aggressive",
         "account_status": "KYC Pending", "relationship_manager": "Arjun Kumar",
         "total_aum": 0, "portfolio_value": 0, "available_cash": 0},
        {"full_name": "Vikram Nair", "phone": "9876501005", "email": "vikram.n@email.com",
         "pan_number": "MNOBN7890E", "city": "Chennai", "state": "Tamil Nadu",
         "client_type": "HUF", "risk_profile": "Very Aggressive",
         "account_status": "Account Active", "relationship_manager": "Priya Sharma",
         "total_aum": 5000000, "portfolio_value": 5650000, "available_cash": 300000,
         "total_pnl": 650000},
    ]

    for cd in clients_data:
        if not frappe.db.exists("Stock Client", {"full_name": cd["full_name"]}):
            doc = frappe.new_doc("Stock Client")
            for k, v in cd.items():
                setattr(doc, k, v)
            doc.is_active = 1
            doc.onboarding_date = add_days(today(), -90)
            doc.activation_date = add_days(today(), -60) if cd["account_status"] == "Account Active" else None
            doc.insert(ignore_permissions=True)

    print(f"  Created {len(clients_data)} sample clients")

    # KYC for active clients
    _create_sample_kyc()
    # Orders
    _create_sample_orders()
    # Margin call
    _create_sample_margin_call()
    # Contract notes
    _create_sample_contract_notes()


def _create_sample_kyc():
    if not frappe.db.table_exists("tabStock KYC"):
        return
    clients = frappe.get_all("Stock Client", filters={"account_status": "Account Active"},
        fields=["full_name", "pan_number"], limit=3)
    for c in clients:
        if not frappe.db.exists("Stock KYC", {"client_name": c.full_name}):
            doc = frappe.new_doc("Stock KYC")
            doc.client_name = c.full_name
            doc.client_pan = c.pan_number
            doc.kyc_date = add_days(today(), -60)
            doc.kyc_type = "Video KYC"
            doc.kyc_status = "Verified"
            doc.verified_by = "Administrator"
            doc.verified_on = add_days(today(), -58)
            doc.expiry_date = add_days(today(), 305)
            doc.pan_verified = 1
            doc.aadhaar_verified = 1
            doc.address_verified = 1
            doc.bank_verified = 1
            doc.video_kyc_done = 1
            doc.insert(ignore_permissions=True)
    print("  KYC records created")


def _create_sample_orders():
    if not frappe.db.table_exists("tabStock Order"):
        return
    clients = frappe.get_all("Stock Client", filters={"account_status": "Account Active"},
        fields=["full_name"], limit=3)
    orders = [
        ("RELIANCE", "NSE", "Buy", "Limit", "CNC", 10, 2840.00, "Executed"),
        ("TCS", "NSE", "Sell", "Market", "MIS", 5, 3415.00, "Executed"),
        ("INFY", "NSE", "Buy", "Limit", "CNC", 20, 1450.00, "Open"),
        ("HDFCBANK", "NSE", "Buy", "Limit", "CNC", 15, 1720.00, "Placed"),
        ("SBIN", "NSE", "Buy", "Market", "MIS", 50, 810.00, "Executed"),
    ]
    for i, (sym, exch, trade, otype, prod, qty, price, status) in enumerate(orders):
        client = clients[i % len(clients)].full_name
        doc = frappe.new_doc("Stock Order")
        doc.client_name = client
        doc.order_date = today()
        doc.symbol = sym
        doc.exchange = exch
        doc.trade_type = trade
        doc.order_type = otype
        doc.product_type = prod
        doc.quantity = qty
        doc.price = price
        doc.segment = "Equity"
        doc.status = status
        doc.validity = "Day"
        if status == "Executed":
            doc.executed_quantity = qty
            doc.executed_price = price
            doc.executed_value = qty * price
        doc.insert(ignore_permissions=True)
    print("  Sample orders created")


def _create_sample_margin_call():
    if not frappe.db.table_exists("tabStock Margin Call"):
        return
    clients = frappe.get_all("Stock Client", filters={"account_status": "Account Active"},
        fields=["full_name", "phone"], limit=1)
    if clients:
        c = clients[0]
        if not frappe.db.exists("Stock Margin Call", {"client_name": c.full_name, "response_received": 0}):
            doc = frappe.new_doc("Stock Margin Call")
            doc.client_name = c.full_name
            doc.client_phone = c.phone
            doc.call_date = today()
            doc.shortfall_amount = 45000
            doc.current_margin = 80000
            doc.required_margin = 125000
            doc.utilization_percent = 85.5
            doc.positions_at_risk = "RELIANCE x 10, TCS x 5"
            doc.whatsapp_sent = 0
            doc.response_received = 0
            doc.insert(ignore_permissions=True)
            print("  Margin call created")


def _create_sample_contract_notes():
    if not frappe.db.table_exists("tabStock Contract Note"):
        return
    clients = frappe.get_all("Stock Client", filters={"account_status": "Account Active"},
        fields=["full_name", "pan_number"], limit=2)
    for i, c in enumerate(clients):
        doc = frappe.new_doc("Stock Contract Note")
        doc.client_name = c.full_name
        doc.client_pan = c.pan_number
        doc.contract_date = add_days(today(), -i)
        doc.settlement_number = f"2024T+1{i+1:04d}"
        doc.settlement_type = "T+1"
        doc.exchange = "NSE"
        doc.segment = "Equity"
        doc.total_buy_trades = 2
        doc.total_sell_trades = 1
        doc.total_buy_quantity = 25
        doc.total_sell_quantity = 5
        doc.total_buy_value = 45000
        doc.total_sell_value = 17000
        doc.gross_turnover = 62000
        doc.net_obligation = 28000
        doc.net_obligation_type = "Pay-In"
        doc.brokerage = 40
        doc.total_stt = 62
        doc.total_charges = 180
        doc.net_payable = 28180
        doc.due_date = add_days(today(), 1)
        doc.payment_status = "Pending"
        doc.insert(ignore_permissions=True)
    print("  Contract notes created")
=======


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
>>>>>>> 1d8b324a77ed9333e48a012b11446f488c4a4b47
