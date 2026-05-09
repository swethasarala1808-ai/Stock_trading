frappe.ui.form.on("Stock Trade", {
    refresh(frm) {
        if (frm.doc.status === "Pending" && !frm.is_new()) {
            frm.add_custom_button(__("Execute Trade"), () => {
                frappe.confirm(
                    `Are you sure you want to execute this ${frm.doc.trade_type} trade for ${frm.doc.quantity} shares of ${frm.doc.symbol}?`,
                    () => {
                        frm.savesubmit();
                    }
                );
            }, __("Actions")).addClass("btn-primary");
        }

        if (!frm.is_new() && frm.doc.symbol) {
            frm.add_custom_button(__("Get Live Quote"), () => {
                frappe.call({
                    method: "stock_app.api.stock_api.get_stock_quote",
                    args: { symbol: frm.doc.symbol },
                    callback(r) {
                        if (r.message) {
                            const q = r.message;
                            frappe.msgprint({
                                title: `${q.symbol} — Live Quote`,
                                message: `
                                    <b>Price:</b> ₹${q.price.toFixed(2)}<br>
                                    <b>Change:</b> ${q.change >= 0 ? "▲" : "▼"} ₹${Math.abs(q.change).toFixed(2)} (${q.change_percent.toFixed(2)}%)<br>
                                    <b>High:</b> ₹${q.high} &nbsp; <b>Low:</b> ₹${q.low}<br>
                                    <b>Volume:</b> ${q.volume?.toLocaleString()}<br>
                                    <small>Source: ${q.source}</small>
                                `,
                                indicator: q.change >= 0 ? "green" : "red",
                            });

                            if (!frm.doc.price_per_share) {
                                frm.set_value("price_per_share", q.price);
                            }
                        }
                    },
                });
            });
        }
    },

    quantity(frm) { calculate_amounts(frm); },
    price_per_share(frm) { calculate_amounts(frm); },
    brokerage_fee(frm) { calculate_amounts(frm); },

    symbol(frm) {
        if (frm.doc.symbol) {
            frm.set_value("symbol", frm.doc.symbol.toUpperCase());
        }
    },
});

function calculate_amounts(frm) {
    const qty = frm.doc.quantity || 0;
    const price = frm.doc.price_per_share || 0;
    const fee = frm.doc.brokerage_fee || 0;
    const total = qty * price;

    frm.set_value("total_amount", total);
    frm.set_value(
        "net_amount",
        frm.doc.trade_type === "Buy" ? total + fee : total - fee
    );
}
