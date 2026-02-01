app_name = "jewelry"
app_title = "Jewelry"
app_publisher = "Your Name"
app_description = "Jewelry Dynamic Pricing Module for ERPNext"
app_email = "your@email.com"
app_license = "MIT"

# Apps
# Note: removed required_apps to avoid GitHub API validation
# This app depends on frappe and erpnext being installed

# DocType Events
doc_events = {
    "Sales Order": {
        "validate": "jewelry.utils.pricing.calculate_jewelry_prices"
    },
    "Sales Invoice": {
        "validate": "jewelry.utils.pricing.calculate_jewelry_prices"
    },
    "Quotation": {
        "validate": "jewelry.utils.pricing.calculate_jewelry_prices"
    },
    "POS Invoice": {
        "validate": "jewelry.utils.pricing.calculate_jewelry_prices"
    }
}

# DocType JS
doctype_js = {
    "Item": "public/js/item.js"
}

# Fixtures - Export custom fields
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["name", "in", [
            "Item-is_jewelry",
            "Item-metal_type",
            "Item-net_weight",
            "Item-making_charge_type",
            "Item-making_charge",
            "Item-jewelry_section"
        ]]]
    }
]

# After Install
after_install = "jewelry.jewelry.custom_fields.create_custom_fields_for_jewelry"
