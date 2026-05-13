frappe.ui.form.on("Market Watchlist", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Refresh Quotes"), () => {
                frappe.call({
                    method: "stock_app.api.stock_api.get_watchlist_quotes",
                    args: { watchlist_name: frm.doc.name },
                    callback(r) {
                        if (r.message && r.message.length) {
                            r.message.forEach((q) => {
                                (frm.doc.stocks || []).forEach((row) => {
                                    if (row.symbol === q.symbol) {
                                        frappe.model.set_value(row.doctype, row.name, "last_price", q.price);
                                        frappe.model.set_value(row.doctype, row.name, "change_percent", q.change_percent);
                                    }
                                });
                            });
                            frm.refresh_field("stocks");
                            frappe.show_alert({ message: "Quotes refreshed!", indicator: "green" });
                        }
                    },
                });
            }, __("Actions"));
        }
    },
});
