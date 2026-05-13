import frappe

@frappe.whitelist(allow_guest=True)
def submit_account_opening(full_name, phone, email="", city="", pan="",
                            investment_range="", goal="", preferred_time="", notes=""):
    try:
        if not full_name or not phone:
            return {"success": False, "error": "Name and phone are required"}
        doc = frappe.new_doc("Stock Client")
        doc.full_name = full_name
        doc.phone = phone
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
        return {"success": True, "message": "Application received! Our RM will call you within 2 hours."}
    except Exception as e:
        frappe.log_error(str(e), "submit_account_opening")
        return {"success": False, "error": "Something went wrong. Please call us at 040-12345678"}

@frappe.whitelist(allow_guest=True)
def get_public_stats():
    try:
        aum = frappe.db.sql("SELECT IFNULL(SUM(total_aum),0) FROM `tabStock Client` WHERE account_status='Account Active'")[0][0]
        clients = frappe.db.count("Stock Client", {"account_status": "Account Active"})
        return {"total_aum": float(aum or 0), "active_clients": clients, "exchanges": 2, "years": 5}
    except Exception:
        return {"total_aum": 0, "active_clients": 0, "exchanges": 2, "years": 5}

@frappe.whitelist(allow_guest=False)
def get_dashboard_stats():
    try:
        today = frappe.utils.today()
        return {
            "total_clients": frappe.db.count("Stock Client"),
            "active_clients": frappe.db.count("Stock Client", {"account_status": "Account Active"}),
            "total_aum": float(frappe.db.sql("SELECT IFNULL(SUM(total_aum),0) FROM `tabStock Client`")[0][0] or 0),
            "today_turnover": float(frappe.db.sql("SELECT IFNULL(SUM(trade_value),0) FROM `tabStock Trade Book` WHERE trade_date=%s", today)[0][0] or 0),
            "orders_today": frappe.db.count("Stock Order", {"order_date": today}),
            "executed_today": frappe.db.count("Stock Order", {"order_date": today, "status": "Executed"}),
            "pending_kyc": frappe.db.count("Stock Client", {"account_status": ["in", ["Application Received","KYC Pending"]]}),
            "margin_calls": frappe.db.count("Stock Margin Call", {"response_received": 0}),
            "monthly_brokerage": float(frappe.db.sql("SELECT IFNULL(SUM(brokerage),0) FROM `tabStock Trade Book` WHERE trade_date>=%s", frappe.utils.get_first_day(today))[0][0] or 0),
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
        if exchange and exchange != "All": filters["exchange"] = exchange
        if search:
            return frappe.db.sql(
                "SELECT name,symbol,company_name,exchange,last_price,open_price,high_price,low_price,prev_close,day_change,day_change_percent,volume,fifty_two_week_high,fifty_two_week_low,market_cap FROM `tabStock Market Watch` WHERE is_active=1 AND (symbol LIKE %s OR company_name LIKE %s) LIMIT %s",
                (f"%{search}%",f"%{search}%",int(limit)), as_dict=1)
        return frappe.get_all("Stock Market Watch", filters=filters,
            fields=["name","symbol","company_name","exchange","last_price","open_price","high_price",
                    "low_price","prev_close","day_change","day_change_percent","volume",
                    "fifty_two_week_high","fifty_two_week_low","market_cap"],
            order_by="symbol", limit=int(limit))
    except Exception: return []

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
        msg = f"⚠️ *URGENT: Margin Call*\nDear *{client_name}*,\nYour margin utilisation has crossed the threshold.\nPlease add funds immediately to avoid auto square-off.\n📞 {s.get('phone','')}\n*{s.get('company_name','Bizaxl Securities')}*"
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
        msg = f"✅ *Trade Confirmed!*\nDear *{t.client_name}*,\n{t.trade_type}: *{t.quantity} shares* of *{t.symbol}*\nPrice: ₹{float(t.price or 0):,.2f} | Net: ₹{float(t.net_amount or 0):,.0f}\nTrade ID: {t.trade_id or t.name}\n*{s.get('company_name','Bizaxl Securities')}*"
        return {"success": True, "wa_url": _wa(phone, msg)}
    except Exception as e: return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=False)
def send_contract_note_alert(contract_note_name):
    try:
        cn = frappe.get_doc("Stock Contract Note", contract_note_name); s = get_settings()
        c = frappe.get_all("Stock Client", filters={"full_name": cn.client_name}, fields=["phone"], limit=1)
        phone = c[0].phone if c else ""
        msg = f"📄 *Contract Note — {cn.settlement_number}*\nDear *{cn.client_name}*,\nDate: {cn.contract_date} | Exchange: {cn.exchange}\nNet: *₹{float(cn.net_payable or 0):,.0f}*\n*{s.get('company_name','Bizaxl Securities')}*"
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
            msg = f"📊 *Monthly Statement — {month} {now.year}*\nDear *{c.full_name}*,\n💼 Portfolio: *₹{float(c.portfolio_value or 0):,.0f}*\n📈 P&L: *{sign}₹{abs(pnl):,.0f}*\n💵 Cash: *₹{float(c.available_cash or 0):,.0f}*\n*{company}*"
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
