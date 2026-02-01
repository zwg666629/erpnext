frappe.query_reports["Jewelry Sales Profit"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("开始日期"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("结束日期"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "customer",
            "label": __("客户"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "item_code",
            "label": __("物料"),
            "fieldtype": "Link",
            "options": "Item",
            "get_query": function() {
                return {
                    filters: {
                        "is_jewelry": 1
                    }
                }
            }
        },
        {
            "fieldname": "metal_type",
            "label": __("金属类型"),
            "fieldtype": "Select",
            "options": "\n足金999\n足金990\n18K金\n22K金\n铂金\n银"
        }
    ]
};
