import frappe
import json
import random

# ─── PUBLIC ───────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_public_stats():
    try:
        aum = frappe.db.sql("SELECT IFNULL(SUM(total_aum),0) FROM `tabStock Client` WHERE account_status='Account Active'")[0][0]
        clients = frappe.db.count("Stock Client", {"account_status": "Account Active"})
        return {"total_aum": float(aum or 0), "active_clients": clients, "exchanges": 2, "years": 5}
    except Exception:
        return {"total_aum": 0, "active_clients": 0, "exchanges": 2, "years": 5}


@frappe.whitelist(allow_guest=True)
def send_otp(phone):
    """Send OTP to phone for eKYC verification"""
    try:
        phone = str(phone).strip().replace(" ", "").replace("-", "")
        if not phone or len(phone) < 10:
            return {"success": False, "error": "Invalid phone number"}
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        # Store in cache for 10 minutes
        cache_key = f"kyc_otp_{phone}"
        frappe.cache().set_value(cache_key, otp, expires_in_sec=600)
        # Log OTP (in production, send via SMS gateway)
        frappe.log_error(f"OTP for {phone}: {otp}", "KYC OTP")
        # In production: send SMS via Twilio/MSG91/etc
        # For demo: return OTP in response (REMOVE in production)
        return {"success": True, "message": f"OTP sent to {phone[-4:].zfill(10)[:6]}****{phone[-4:]}", "demo_otp": otp}
    except Exception as e:
        frappe.log_error(str(e), "send_otp")
        return {"success": False, "error": "Failed to send OTP"}


@frappe.whitelist(allow_guest=True)
def verify_otp(phone, otp):
    """Verify OTP for eKYC"""
    try:
        phone = str(phone).strip()
        cache_key = f"kyc_otp_{phone}"
        stored_otp = frappe.cache().get_value(cache_key)
        if not stored_otp:
            return {"success": False, "error": "OTP expired. Please request a new one."}
        if str(otp).strip() == str(stored_otp):
            frappe.cache().delete_value(cache_key)
            # Mark phone as verified in cache for 30 mins
            frappe.cache().set_value(f"phone_verified_{phone}", 1, expires_in_sec=1800)
            return {"success": True, "message": "Phone verified successfully!"}
        return {"success": False, "error": "Invalid OTP. Please try again."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def verify_pan(pan, name):
    """Simulate PAN verification (integrate with NSDL/CDSL API in production)"""
    try:
        pan = str(pan).strip().upper()
        if not pan or len(pan) != 10:
            return {"success": False, "error": "Invalid PAN format"}
        import re
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan):
            return {"success": False, "error": "Invalid PAN format. Should be like ABCDE1234F"}
        # Simulate API verification
        return {"success": True, "verified": True, "message": "PAN verified successfully", "pan_name": name.upper()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def verify_bank(ifsc, account_number, account_holder):
    """Simulate bank account penny drop verification"""
    try:
        ifsc = str(ifsc).strip().upper()
        if not ifsc or len(ifsc) != 11:
            return {"success": False, "error": "Invalid IFSC code"}
        # Simulate penny drop
        bank_names = {
            "HDFC": "HDFC Bank", "SBIN": "State Bank of India",
            "ICIC": "ICICI Bank", "KKBK": "Kotak Mahindra Bank",
            "AXIS": "Axis Bank", "PUNB": "Punjab National Bank",
            "UBIN": "Union Bank of India", "CNRB": "Canara Bank"
        }
        bank_code = ifsc[:4]
        bank_name = bank_names.get(bank_code, "Bank")
        return {
            "success": True, "verified": True,
            "message": f"Bank account verified via penny drop",
            "bank_name": bank_name, "branch": "Main Branch",
            "account_holder": account_holder.upper()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def submit_account_opening(full_name, phone, email="", city="", pan="",
                            investment_range="", goal="", preferred_time="", notes=""):
    try:
        if not full_name or not phone:
            return {"success": False, "error": "Name and phone are required"}

        # Check phone verified
        phone_clean = str(phone).strip()
        verified = frappe.cache().get_value(f"phone_verified_{phone_clean}")
        if not verified:
            return {"success": False, "error": "Phone not verified. Please complete OTP verification first."}

        # Check duplicate
        if frappe.db.exists("Stock Client", {"phone": phone_clean}):
            return {"success": False, "error": "Account with this phone already exists. Please login or call us."}

        doc = frappe.new_doc("Stock Client")
        doc.full_name = full_name
        doc.phone = phone_clean
        doc.email = email
        doc.city = city
        doc.pan_number = pan.upper() if pan else ""
        doc.annual_income = investment_range
        doc.account_status = "Application Received"
        doc.onboarding_date = frappe.utils.today()
        doc.is_active = 1
        doc.notes = notes or f"Goal: {goal} | Preferred Time: {preferred_time}"
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Notify RM
        s = get_settings()
        wa_num = s.get("whatsapp_number", "")
        if wa_num:
            import urllib.parse
            rm_msg = f"🎉 New Application!\nName: {full_name}\nPhone: {phone}\nPAN: {pan}\nCity: {city}\nGoal: {goal}"
            frappe.log_error(f"https://wa.me/91{wa_num}?text={urllib.parse.quote(rm_msg)}", "New Application")

        return {"success": True, "message": "Application received! Our RM will call you within 2 hours for Video KYC.", "client_id": doc.name}
    except Exception as e:
        frappe.log_error(str(e), "submit_account_opening")
        return {"success": False, "error": "Something went wrong. Please call us at 040-12345678"}


# ─── SEED SAMPLE DATA ─────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def seed_sample_data():
    """Add sample market watch data"""
    try:
        stocks = [
            {"symbol":"RELIANCE","company_name":"Reliance Industries Ltd","exchange":"NSE","sector":"Energy","last_price":2847.50,"open_price":2820.00,"high_price":2865.00,"low_price":2810.00,"prev_close":2824.00,"day_change":23.50,"day_change_percent":0.83,"volume":8234567,"fifty_two_week_high":3027.00,"fifty_two_week_low":2220.30,"market_cap":1928000000000},
            {"symbol":"TCS","company_name":"Tata Consultancy Services","exchange":"NSE","sector":"IT","last_price":3412.20,"open_price":3445.00,"high_price":3460.00,"low_price":3398.00,"prev_close":3430.80,"day_change":-18.60,"day_change_percent":-0.54,"volume":3421890,"fifty_two_week_high":4592.25,"fifty_two_week_low":3056.05,"market_cap":1245000000000},
            {"symbol":"HDFCBANK","company_name":"HDFC Bank Ltd","exchange":"NSE","sector":"Banking","last_price":1723.40,"open_price":1735.00,"high_price":1748.00,"low_price":1718.50,"prev_close":1731.75,"day_change":-8.35,"day_change_percent":-0.48,"volume":12456789,"fifty_two_week_high":1880.00,"fifty_two_week_low":1363.55,"market_cap":1312000000000},
            {"symbol":"ICICIBANK","company_name":"ICICI Bank Ltd","exchange":"NSE","sector":"Banking","last_price":1187.30,"open_price":1172.00,"high_price":1195.00,"low_price":1168.00,"prev_close":1171.95,"day_change":15.35,"day_change_percent":1.31,"volume":18923456,"fifty_two_week_high":1196.00,"fifty_two_week_low":892.00,"market_cap":838000000000},
            {"symbol":"SBIN","company_name":"State Bank of India","exchange":"NSE","sector":"Banking","last_price":812.75,"open_price":802.00,"high_price":818.00,"low_price":799.50,"prev_close":803.05,"day_change":9.70,"day_change_percent":1.21,"volume":22345678,"fifty_two_week_high":912.00,"fifty_two_week_low":600.35,"market_cap":725000000000},
            {"symbol":"INFY","company_name":"Infosys Ltd","exchange":"NSE","sector":"IT","last_price":1654.80,"open_price":1667.00,"high_price":1672.00,"low_price":1648.00,"prev_close":1662.40,"day_change":-7.60,"day_change_percent":-0.46,"volume":6789012,"fifty_two_week_high":1953.90,"fifty_two_week_low":1307.30,"market_cap":689000000000},
            {"symbol":"WIPRO","company_name":"Wipro Ltd","exchange":"NSE","sector":"IT","last_price":487.25,"open_price":480.00,"high_price":492.00,"low_price":478.50,"prev_close":484.10,"day_change":3.15,"day_change_percent":0.65,"volume":5234567,"fifty_two_week_high":562.35,"fifty_two_week_low":380.25,"market_cap":254000000000},
            {"symbol":"BAJFINANCE","company_name":"Bajaj Finance Ltd","exchange":"NSE","sector":"Banking","last_price":7234.50,"open_price":7180.00,"high_price":7290.00,"low_price":7160.00,"prev_close":7198.75,"day_change":35.75,"day_change_percent":0.50,"volume":1234567,"fifty_two_week_high":8192.00,"fifty_two_week_low":6187.80,"market_cap":437000000000},
            {"symbol":"TATAMOTORS","company_name":"Tata Motors Ltd","exchange":"NSE","sector":"Auto","last_price":934.60,"open_price":920.00,"high_price":942.00,"low_price":916.00,"prev_close":928.35,"day_change":6.25,"day_change_percent":0.67,"volume":14567890,"fifty_two_week_high":1179.00,"fifty_two_week_low":635.05,"market_cap":344000000000},
            {"symbol":"MARUTI","company_name":"Maruti Suzuki India","exchange":"NSE","sector":"Auto","last_price":12456.00,"open_price":12300.00,"high_price":12520.00,"low_price":12250.00,"prev_close":12389.50,"day_change":66.50,"day_change_percent":0.54,"volume":456789,"fifty_two_week_high":13680.00,"fifty_two_week_low":9737.80,"market_cap":376000000000},
            {"symbol":"SUNPHARMA","company_name":"Sun Pharmaceutical","exchange":"NSE","sector":"Pharma","last_price":1834.75,"open_price":1820.00,"high_price":1848.00,"low_price":1815.00,"prev_close":1828.40,"day_change":6.35,"day_change_percent":0.35,"volume":3456789,"fifty_two_week_high":1960.35,"fifty_two_week_low":1310.00,"market_cap":440000000000},
            {"symbol":"DRREDDY","company_name":"Dr Reddy's Laboratories","exchange":"NSE","sector":"Pharma","last_price":6123.40,"open_price":6080.00,"high_price":6145.00,"low_price":6065.00,"prev_close":6098.20,"day_change":25.20,"day_change_percent":0.41,"volume":678901,"fifty_two_week_high":6748.00,"fifty_two_week_low":4856.00,"market_cap":102000000000},
            {"symbol":"ONGC","company_name":"Oil & Natural Gas Corp","exchange":"NSE","sector":"Energy","last_price":267.45,"open_price":264.00,"high_price":269.50,"low_price":262.00,"prev_close":265.80,"day_change":1.65,"day_change_percent":0.62,"volume":23456789,"fifty_two_week_high":345.00,"fifty_two_week_low":183.00,"market_cap":336000000000},
            {"symbol":"NTPC","company_name":"NTPC Ltd","exchange":"NSE","sector":"Energy","last_price":389.20,"open_price":384.00,"high_price":392.00,"low_price":382.50,"prev_close":386.45,"day_change":2.75,"day_change_percent":0.71,"volume":9876543,"fifty_two_week_high":448.45,"fifty_two_week_low":280.05,"market_cap":378000000000},
            {"symbol":"TATASTEEL","company_name":"Tata Steel Ltd","exchange":"NSE","sector":"Metal","last_price":167.80,"open_price":165.00,"high_price":169.50,"low_price":164.50,"prev_close":166.35,"day_change":1.45,"day_change_percent":0.87,"volume":34567890,"fifty_two_week_high":184.60,"fifty_two_week_low":119.00,"market_cap":210000000000},
            {"symbol":"HINDALCO","company_name":"Hindalco Industries","exchange":"NSE","sector":"Metal","last_price":678.90,"open_price":670.00,"high_price":684.00,"low_price":667.00,"prev_close":673.25,"day_change":5.65,"day_change_percent":0.84,"volume":8901234,"fifty_two_week_high":772.65,"fifty_two_week_low":466.15,"market_cap":153000000000},
            {"symbol":"ITC","company_name":"ITC Ltd","exchange":"NSE","sector":"FMCG","last_price":456.30,"open_price":452.00,"high_price":459.00,"low_price":450.00,"prev_close":454.80,"day_change":1.50,"day_change_percent":0.33,"volume":12345678,"fifty_two_week_high":528.50,"fifty_two_week_low":401.70,"market_cap":571000000000},
            {"symbol":"HINDUNILVR","company_name":"Hindustan Unilever","exchange":"NSE","sector":"FMCG","last_price":2345.60,"open_price":2330.00,"high_price":2360.00,"low_price":2320.00,"prev_close":2338.90,"day_change":6.70,"day_change_percent":0.29,"volume":2345678,"fifty_two_week_high":2700.00,"fifty_two_week_low":2172.00,"market_cap":551000000000},
            {"symbol":"LT","company_name":"Larsen & Toubro Ltd","exchange":"NSE","sector":"Infrastructure","last_price":3567.80,"open_price":3540.00,"high_price":3590.00,"low_price":3525.00,"prev_close":3554.30,"day_change":13.50,"day_change_percent":0.38,"volume":1678901,"fifty_two_week_high":3963.00,"fifty_two_week_low":2840.00,"market_cap":491000000000},
            {"symbol":"KOTAKBANK","company_name":"Kotak Mahindra Bank","exchange":"NSE","sector":"Banking","last_price":1987.50,"open_price":1972.00,"high_price":1998.00,"low_price":1966.00,"prev_close":1979.80,"day_change":7.70,"day_change_percent":0.39,"volume":3456789,"fifty_two_week_high":2062.00,"fifty_two_week_low":1543.85,"market_cap":397000000000},
        ]
        added = 0
        for s in stocks:
            if not frappe.db.exists("Stock Market Watch", {"symbol": s["symbol"]}):
                doc = frappe.new_doc("Stock Market Watch")
                for k, v in s.items():
                    if hasattr(doc, k):
                        setattr(doc, k, v)
                doc.is_active = 1
                doc.insert(ignore_permissions=True)
                added += 1
        frappe.db.commit()
        return {"success": True, "added": added, "message": f"Added {added} stocks to Market Watch"}
    except Exception as e:
        frappe.log_error(str(e), "seed_sample_data")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def seed_sample_clients():
    """Add sample clients"""
    try:
        clients = [
            {"full_name":"Rahul Sharma","phone":"9876543210","email":"rahul@example.com","city":"Mumbai","pan_number":"ABCRS1234P","client_type":"Individual","risk_profile":"Aggressive","account_status":"Account Active","total_aum":2500000,"portfolio_value":2847500,"available_cash":125000,"total_pnl":347500,"relationship_manager":"Priya Mehta"},
            {"full_name":"Priya Patel","phone":"9876543211","email":"priya@example.com","city":"Ahmedabad","pan_number":"BCDPP5678Q","client_type":"Individual","risk_profile":"Moderate","account_status":"Account Active","total_aum":1200000,"portfolio_value":1356000,"available_cash":87500,"total_pnl":156000,"relationship_manager":"Raj Kumar"},
            {"full_name":"Amit Verma","phone":"9876543212","email":"amit@example.com","city":"Delhi","pan_number":"CDEAV9012R","client_type":"Individual","risk_profile":"Conservative","account_status":"KYC Pending","total_aum":500000,"portfolio_value":512000,"available_cash":45000,"total_pnl":12000,"relationship_manager":"Priya Mehta"},
            {"full_name":"Sunita Reddy","phone":"9876543213","email":"sunita@example.com","city":"Hyderabad","pan_number":"DEFSR3456S","client_type":"Individual","risk_profile":"Very Aggressive","account_status":"Account Active","total_aum":5000000,"portfolio_value":6125000,"available_cash":325000,"total_pnl":1125000,"relationship_manager":"Raj Kumar"},
            {"full_name":"Kiran Shah","phone":"9876543214","email":"kiran@example.com","city":"Bangalore","pan_number":"EFGKS7890T","client_type":"HUF","risk_profile":"Moderate","account_status":"Account Active","total_aum":800000,"portfolio_value":856000,"available_cash":56000,"total_pnl":56000,"relationship_manager":"Priya Mehta"},
            {"full_name":"Deepak Nair","phone":"9876543215","email":"deepak@example.com","city":"Chennai","pan_number":"FGHDN2345U","client_type":"Individual","risk_profile":"Aggressive","account_status":"Application Received","total_aum":0,"portfolio_value":0,"available_cash":0,"total_pnl":0,"relationship_manager":""},
            {"full_name":"Ananya Joshi","phone":"9876543216","email":"ananya@example.com","city":"Pune","pan_number":"GHIAJ6789V","client_type":"Individual","risk_profile":"Moderate","account_status":"Account Active","total_aum":950000,"portfolio_value":1018500,"available_cash":68500,"total_pnl":68500,"relationship_manager":"Raj Kumar"},
            {"full_name":"Vikram Singh","phone":"9876543217","email":"vikram@example.com","city":"Jaipur","pan_number":"HIJVS1234W","client_type":"Corporate","risk_profile":"Aggressive","account_status":"Account Active","total_aum":10000000,"portfolio_value":11450000,"available_cash":750000,"total_pnl":1450000,"relationship_manager":"Priya Mehta"},
        ]
        added = 0
        for c in clients:
            if not frappe.db.exists("Stock Client", {"phone": c["phone"]}):
                doc = frappe.new_doc("Stock Client")
                for k, v in c.items():
                    if hasattr(doc, k):
                        setattr(doc, k, v)
                doc.onboarding_date = frappe.utils.today()
                doc.is_active = 1
                doc.insert(ignore_permissions=True)
                added += 1
        frappe.db.commit()
        return {"success": True, "added": added}
    except Exception as e:
        frappe.log_error(str(e), "seed_sample_clients")
        return {"success": False, "error": str(e)}


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=False)
def get_dashboard_stats():
    try:
        today = frappe.utils.today()
        month_start = frappe.utils.get_first_day(today)
        return {
            "total_clients": frappe.db.count("Stock Client"),
            "active_clients": frappe.db.count("Stock Client", {"account_status": "Account Active"}),
            "total_aum": float(frappe.db.sql("SELECT IFNULL(SUM(total_aum),0) FROM `tabStock Client`")[0][0] or 0),
            "today_turnover": float(frappe.db.sql("SELECT IFNULL(SUM(trade_value),0) FROM `tabStock Trade Book` WHERE trade_date=%s", today)[0][0] or 0),
            "orders_today": frappe.db.count("Stock Order", {"order_date": today}),
            "executed_today": frappe.db.count("Stock Order", {"order_date": today, "status": "Executed"}),
            "pending_kyc": frappe.db.count("Stock Client", {"account_status": ["in", ["Application Received","KYC Pending"]]}),
            "margin_calls": frappe.db.count("Stock Margin Call", {"response_received": 0}),
            "monthly_brokerage": float(frappe.db.sql("SELECT IFNULL(SUM(brokerage),0) FROM `tabStock Trade Book` WHERE trade_date>=%s", month_start)[0][0] or 0),
        }
    except Exception as e:
        frappe.log_error(str(e), "get_dashboard_stats")
        return {"total_clients":0,"active_clients":0,"total_aum":0,"today_turnover":0,
                "orders_today":0,"executed_today":0,"pending_kyc":0,"margin_calls":0,"monthly_brokerage":0}


@frappe.whitelist(allow_guest=False)
def get_settings():
    try:
        if not frappe.db.table_exists("tabStock Settings"): return {}
        return frappe.get_single("Stock Settings").as_dict()
    except Exception: return {}


@frappe.whitelist(allow_guest=False)
def save_settings(**kwargs):
    try:
        doc = frappe.get_single("Stock Settings")
        for k, v in kwargs.items():
            if hasattr(doc, k): setattr(doc, k, v)
        doc.save(ignore_permissions=True); frappe.db.commit()
        return {"success": True}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def get_clients(status=None, search=None, limit=50, start=0):
    try:
        if search:
            return frappe.db.sql(
                "SELECT name,full_name,phone,email,pan_number,client_type,risk_profile,account_status,relationship_manager,total_aum,portfolio_value,onboarding_date FROM `tabStock Client` WHERE (full_name LIKE %s OR phone LIKE %s OR pan_number LIKE %s) ORDER BY creation DESC LIMIT %s",
                (f"%{search}%",f"%{search}%",f"%{search}%",int(limit)), as_dict=1)
        filters = {}
        if status: filters["account_status"] = status
        return frappe.get_all("Stock Client", filters=filters,
            fields=["name","full_name","phone","email","pan_number","client_type","risk_profile",
                    "account_status","relationship_manager","total_aum","portfolio_value","onboarding_date"],
            order_by="creation desc", limit=int(limit))
    except Exception as e:
        frappe.log_error(str(e),"get_clients"); return []


@frappe.whitelist(allow_guest=False)
def get_client_detail(client_name):
    try: return frappe.get_doc("Stock Client", client_name).as_dict()
    except Exception: return {}


@frappe.whitelist(allow_guest=False)
def create_client(full_name, phone, email="", pan_number="", client_type="Individual", risk_profile="Moderate"):
    try:
        doc = frappe.new_doc("Stock Client")
        doc.full_name=full_name; doc.phone=phone; doc.email=email
        doc.pan_number=pan_number; doc.client_type=client_type; doc.risk_profile=risk_profile
        doc.account_status="Application Received"; doc.onboarding_date=frappe.utils.today(); doc.is_active=1
        doc.insert(ignore_permissions=True); frappe.db.commit()
        return {"success": True, "name": doc.name}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def update_client_status(client_name, status):
    try:
        frappe.db.set_value("Stock Client", client_name, "account_status", status)
        frappe.db.commit(); return {"success": True}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def get_kyc(client_name):
    try:
        r = frappe.get_all("Stock KYC", filters={"client_name": client_name}, fields=["*"], limit=1)
        return r[0] if r else {}
    except Exception: return {}


@frappe.whitelist(allow_guest=False)
def get_orders(client_name=None, status=None, date_from=None, date_to=None, segment=None, limit=50):
    try:
        filters = {}
        if client_name: filters["client_name"] = client_name
        if status: filters["status"] = status
        if segment: filters["segment"] = segment
        if date_from and date_to: filters["order_date"] = ["between",[date_from,date_to]]
        return frappe.get_all("Stock Order", filters=filters,
            fields=["name","client_name","order_date","symbol","exchange","segment","order_type",
                    "trade_type","product_type","quantity","price","status","executed_quantity",
                    "executed_price","executed_value"],
            order_by="order_date desc,creation desc", limit=int(limit))
    except Exception as e: frappe.log_error(str(e),"get_orders"); return []


@frappe.whitelist(allow_guest=False)
def place_trade(symbol, trade_type, quantity, price_per_share=0, portfolio_name="", brokerage_fee=20, notes=""):
    try:
        doc = frappe.new_doc("Stock Order")
        doc.symbol=symbol; doc.trade_type=trade_type; doc.quantity=int(quantity)
        doc.price=float(price_per_share); doc.order_type="Market" if float(price_per_share)==0 else "Limit"
        doc.order_date=frappe.utils.today(); doc.status="Placed"; doc.remarks=notes
        doc.insert(ignore_permissions=True); frappe.db.commit()
        return {"success": True, "trade_id": doc.name}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def get_trade_book(client_name=None, date_from=None, date_to=None, segment=None, limit=50):
    try:
        filters = {}
        if client_name: filters["client_name"] = client_name
        if segment: filters["segment"] = segment
        if date_from and date_to: filters["trade_date"] = ["between",[date_from,date_to]]
        return frappe.get_all("Stock Trade Book", filters=filters,
            fields=["name","client_name","trade_date","symbol","exchange","trade_type","product_type",
                    "quantity","price","trade_value","brokerage","stt","gst","total_charges","net_amount","trade_id"],
            order_by="trade_date desc", limit=int(limit))
    except Exception: return []


@frappe.whitelist(allow_guest=False)
def get_market_watch(sector=None, exchange=None, search=None, limit=50):
    try:
        filters = {"is_active": 1}
        if sector: filters["sector"] = sector
        if exchange and exchange not in ("All",""): filters["exchange"] = exchange
        if search:
            return frappe.db.sql(
                "SELECT name,symbol,company_name,exchange,last_price,open_price,high_price,low_price,prev_close,day_change,day_change_percent,volume,fifty_two_week_high,fifty_two_week_low,market_cap,sector FROM `tabStock Market Watch` WHERE is_active=1 AND (symbol LIKE %s OR company_name LIKE %s) LIMIT %s",
                (f"%{search}%",f"%{search}%",int(limit)), as_dict=1)
        return frappe.get_all("Stock Market Watch", filters=filters,
            fields=["name","symbol","company_name","exchange","last_price","open_price","high_price",
                    "low_price","prev_close","day_change","day_change_percent","volume",
                    "fifty_two_week_high","fifty_two_week_low","market_cap","sector"],
            order_by="symbol", limit=int(limit))
    except Exception as e:
        frappe.log_error(str(e),"get_market_watch"); return []


@frappe.whitelist(allow_guest=False)
def get_holdings(client_name, instrument_type=None):
    try:
        filters = {"client_name": client_name, "status": "Open"}
        return frappe.get_all("Stock MTM Position", filters=filters,
            fields=["symbol","quantity","avg_cost_price","current_market_price","unrealized_pnl","total_pnl","mtm_value","segment"])
    except Exception: return []


@frappe.whitelist(allow_guest=False)
def get_mtm_positions(client_name, date=None):
    try:
        filters = {"client_name": client_name}
        if date: filters["position_date"] = date
        return frappe.get_all("Stock MTM Position", filters=filters, fields=["*"], order_by="position_date desc")
    except Exception: return []


@frappe.whitelist(allow_guest=False)
def get_margin_calls(is_resolved=None, limit=20):
    try:
        filters = {}
        if is_resolved is not None: filters["response_received"] = 1 if str(is_resolved)=="1" else 0
        return frappe.get_all("Stock Margin Call", filters=filters,
            fields=["name","client_name","client_phone","call_date","shortfall_amount",
                    "utilization_percent","whatsapp_sent","response_received","response_type"],
            order_by="call_date desc", limit=int(limit))
    except Exception: return []


def _wa(phone, msg):
    import urllib.parse
    phone = str(phone).replace("+91","").replace(" ","").replace("-","")
    if not phone.startswith("91"): phone = "91" + phone
    return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"


@frappe.whitelist(allow_guest=False)
def trigger_margin_call_whatsapp(client_name):
    try:
        c = frappe.get_all("Stock Client", filters={"full_name": client_name}, fields=["phone"], limit=1)
        phone = c[0].phone if c else ""
        s = get_settings()
        msg = f"⚠️ *URGENT: Margin Call*\nDear *{client_name}*,\nPlease add funds immediately to avoid auto square-off.\n📞 {s.get('phone','')}\n*{s.get('company_name','Bizaxl Securities')}*"
        url = _wa(phone, msg)
        calls = frappe.get_all("Stock Margin Call", filters={"client_name": client_name, "response_received": 0}, limit=1)
        if calls: frappe.db.set_value("Stock Margin Call", calls[0].name, "whatsapp_sent", 1); frappe.db.commit()
        return {"success": True, "wa_url": url}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def send_trade_confirmation(trade_id):
    try:
        t = frappe.get_doc("Stock Trade Book", trade_id); s = get_settings()
        c = frappe.get_all("Stock Client", filters={"full_name": t.client_name}, fields=["phone"], limit=1)
        phone = c[0].phone if c else ""
        msg = f"✅ *Trade Confirmed!*\nDear *{t.client_name}*,\n{t.trade_type}: *{t.quantity} shares* of *{t.symbol}*\nNet: ₹{float(t.net_amount or 0):,.0f}\n*{s.get('company_name','Bizaxl Securities')}*"
        return {"success": True, "wa_url": _wa(phone, msg)}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def send_contract_note_alert(contract_note_name):
    try:
        cn = frappe.get_doc("Stock Contract Note", contract_note_name); s = get_settings()
        c = frappe.get_all("Stock Client", filters={"full_name": cn.client_name}, fields=["phone"], limit=1)
        phone = c[0].phone if c else ""
        msg = f"📄 *Contract Note*\nDear *{cn.client_name}*,\nNet: *₹{float(cn.net_payable or 0):,.0f}*\n*{s.get('company_name','Bizaxl Securities')}*"
        frappe.db.set_value("Stock Contract Note", contract_note_name, "sent_to_client", 1); frappe.db.commit()
        return {"success": True, "wa_url": _wa(phone, msg)}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def send_kyc_expiry_reminder(client_name):
    try:
        s = get_settings()
        c = frappe.get_all("Stock Client", filters={"full_name": client_name}, fields=["phone"], limit=1)
        phone = c[0].phone if c else ""
        msg = f"📋 *KYC Renewal Required*\nDear *{client_name}*, please update your KYC documents.\n📞 {s.get('phone','')}\n*{s.get('company_name','Bizaxl Securities')}*"
        return {"success": True, "wa_url": _wa(phone, msg)}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def send_monthly_statements():
    try:
        s = get_settings(); company = s.get("company_name","Bizaxl Securities")
        import calendar; from datetime import datetime; now = datetime.now(); month = calendar.month_name[now.month]
        clients = frappe.get_all("Stock Client", filters={"account_status":"Account Active"},
            fields=["full_name","phone","portfolio_value","total_aum","total_pnl","available_cash"])
        sent = 0
        for c in clients:
            pnl = float(c.total_pnl or 0); sign = "+" if pnl>=0 else "-"
            msg = f"📊 *Monthly Statement — {month} {now.year}*\nDear *{c.full_name}*,\n💼 Portfolio: *₹{float(c.portfolio_value or 0):,.0f}*\n📈 P&L: *{sign}₹{abs(pnl):,.0f}*\n*{company}*"
            _wa(c.phone, msg); sent += 1
        return {"success": True, "sent": sent}
    except Exception as e: return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=False)
def get_contract_notes(client_name=None, date_from=None, date_to=None, payment_status=None, limit=20):
    try:
        filters = {}
        if client_name: filters["client_name"] = client_name
        if payment_status: filters["payment_status"] = payment_status
        if date_from and date_to: filters["contract_date"] = ["between",[date_from,date_to]]
        return frappe.get_all("Stock Contract Note", filters=filters,
            fields=["name","client_name","contract_date","settlement_number","settlement_type","exchange",
                    "gross_turnover","brokerage","total_stt","total_gst","total_charges","net_payable","due_date","payment_status"],
            order_by="contract_date desc", limit=int(limit))
    except Exception: return []


@frappe.whitelist(allow_guest=False)
def get_invoices(client_name=None, payment_status=None, limit=20):
    try:
        filters = {}
        if client_name: filters["client_name"] = client_name
        if payment_status: filters["payment_status"] = payment_status
        return frappe.get_all("Stock Tax Invoice", filters=filters,
            fields=["name","client_name","invoice_date","invoice_number","subtotal","total_amount",
                    "cgst_amount","sgst_amount","igst_amount","total_gst","payment_status","balance_due"],
            order_by="invoice_date desc", limit=int(limit))
    except Exception: return []


@frappe.whitelist(allow_guest=False)
def get_ledger(client_name, date_from=None, date_to=None, limit=50):
    try:
        filters = {"client_name": client_name}
        if date_from and date_to: filters["entry_date"] = ["between",[date_from,date_to]]
        return frappe.get_all("Stock Ledger Entry", filters=filters,
            fields=["name","entry_date","value_date","narration","entry_type","segment",
                    "debit_amount","credit_amount","closing_balance","reference_number"],
            order_by="entry_date desc", limit=int(limit))
    except Exception: return []
