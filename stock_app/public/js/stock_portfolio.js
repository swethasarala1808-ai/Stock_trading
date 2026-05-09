frappe.ui.form.on("Stock Portfolio", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Recalculate Totals"), () => {
                frm.call("calculate_totals").then(() => {
                    frm.save();
                    frappe.show_alert({ message: "Portfolio totals updated!", indicator: "green" });
                });
            }, __("Actions"));

            frm.add_custom_button(__("View Dashboard"), () => {
                window.open("/stock_dashboard", "_blank");
            });
        }
    },
});
