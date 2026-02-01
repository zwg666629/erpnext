import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("日期"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("发票编号"),
            "fieldname": "invoice",
            "fieldtype": "Link",
            "options": "POS Invoice",
            "width": 150
        },
        {
            "label": _("客户"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": _("物料代码"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": _("物料名称"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("金属类型"),
            "fieldname": "metal_type",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("克重"),
            "fieldname": "net_weight",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": _("数量"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 60
        },
        {
            "label": _("售价"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("成本"),
            "fieldname": "cost",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("毛利润"),
            "fieldname": "profit",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("利润率"),
            "fieldname": "profit_rate",
            "fieldtype": "Percent",
            "width": 80
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            pi.posting_date,
            pi.name as invoice,
            pi.customer,
            pii.item_code,
            pii.item_name,
            item.metal_type,
            item.net_weight,
            pii.qty,
            pii.amount,
            (item.total_cost * pii.qty) as cost
        FROM `tabPOS Invoice` pi
        INNER JOIN `tabPOS Invoice Item` pii ON pii.parent = pi.name
        LEFT JOIN `tabItem` item ON item.name = pii.item_code
        WHERE pi.docstatus = 1
        AND item.is_jewelry = 1
        {conditions}
        ORDER BY pi.posting_date DESC, pi.name
    """.format(conditions=conditions), filters, as_dict=1)

    result = []
    for row in data:
        cost = flt(row.cost) or 0
        amount = flt(row.amount) or 0
        profit = amount - cost
        profit_rate = (profit / cost * 100) if cost > 0 else 0

        result.append({
            "posting_date": row.posting_date,
            "invoice": row.invoice,
            "customer": row.customer,
            "item_code": row.item_code,
            "item_name": row.item_name,
            "metal_type": row.metal_type,
            "net_weight": row.net_weight,
            "qty": row.qty,
            "amount": amount,
            "cost": cost,
            "profit": profit,
            "profit_rate": profit_rate
        })

    return result


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND pi.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND pi.posting_date <= %(to_date)s"

    if filters.get("customer"):
        conditions += " AND pi.customer = %(customer)s"

    if filters.get("item_code"):
        conditions += " AND pii.item_code = %(item_code)s"

    if filters.get("metal_type"):
        conditions += " AND item.metal_type = %(metal_type)s"

    return conditions
