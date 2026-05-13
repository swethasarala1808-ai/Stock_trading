app_name = "stock_app"
app_title = "Stock Trading & Brokerage"
app_publisher = "Swetha Sarala"
app_description = "Stock Trading and Brokerage Management Platform"
app_email = "swethasarala1808@gmail.com"
app_license = "MIT"
app_version = "1.0.0"

after_install = "stock_app.install.after_install"

website_route_rules = [
    {"from_route": "/stock", "to_route": "stock"},
    {"from_route": "/stock-dashboard", "to_route": "stock-dashboard"},
]
