import frappe
from frappe import _


def get_daily_gold_price(metal_type, date=None):
    """
    Get gold price for a specific metal type

    Args:
        metal_type: Metal type (足金999/足金990/18K金/22K金/铂金/银)
        date: Date to get price for (defaults to today)

    Returns:
        float: Price per gram
    """
    from jewelry.jewelry.doctype.daily_gold_price.daily_gold_price import get_gold_price_for_date
    return get_gold_price_for_date(date, metal_type)


def calculate_jewelry_price(item_code, qty=1, date=None):
    """
    Calculate jewelry price and profit for a single item

    Args:
        item_code: Item code
        qty: Quantity
        date: Date for gold price (defaults to today)

    Returns:
        dict: {unit_price, total_price, gold_price, making_charge, cost, profit, profit_rate, breakdown}
    """
    item = frappe.get_doc("Item", item_code)

    if not item.get("is_jewelry"):
        return None

    metal_type = item.get("metal_type")
    net_weight = float(item.get("net_weight") or 0)
    making_charge_type = item.get("making_charge_type")
    making_charge = float(item.get("making_charge") or 0)

    if not metal_type or not net_weight:
        return None

    # Get today's gold price
    gold_price_per_gram = get_daily_gold_price(metal_type, date)

    if not gold_price_per_gram:
        frappe.msgprint(
            _("未找到 {0} 的今日金价，请先录入每日金价").format(metal_type),
            alert=True
        )
        return None

    # Calculate selling price
    base_price = gold_price_per_gram * net_weight

    if making_charge_type == "按克":
        total_making_charge = making_charge * net_weight
    else:  # 按件
        total_making_charge = making_charge

    unit_price = base_price + total_making_charge
    total_price = unit_price * qty

    # Calculate cost
    gold_cost_price = float(item.get("gold_cost_price") or 0)
    making_cost = float(item.get("making_cost") or 0)
    other_cost = float(item.get("other_cost") or 0)

    gold_cost = gold_cost_price * net_weight
    total_cost = gold_cost + making_cost + other_cost

    # Calculate profit
    unit_profit = unit_price - total_cost
    total_profit = unit_profit * qty
    profit_rate = (unit_profit / total_cost * 100) if total_cost > 0 else 0

    return {
        "unit_price": unit_price,
        "total_price": total_price,
        "gold_price_per_gram": gold_price_per_gram,
        "net_weight": net_weight,
        "base_price": base_price,
        "making_charge": total_making_charge,
        # Cost info
        "gold_cost_price": gold_cost_price,
        "gold_cost": gold_cost,
        "making_cost": making_cost,
        "other_cost": other_cost,
        "total_cost": total_cost,
        # Profit info
        "unit_profit": unit_profit,
        "total_profit": total_profit,
        "profit_rate": profit_rate,
        "breakdown": _("{0} × {1}克 + 工费{2} = {3}").format(
            frappe.format_value(gold_price_per_gram, {"fieldtype": "Currency"}),
            net_weight,
            frappe.format_value(total_making_charge, {"fieldtype": "Currency"}),
            frappe.format_value(unit_price, {"fieldtype": "Currency"})
        ),
        "profit_breakdown": _("售价{0} - 成本{1} = 利润{2} ({3}%)").format(
            frappe.format_value(unit_price, {"fieldtype": "Currency"}),
            frappe.format_value(total_cost, {"fieldtype": "Currency"}),
            frappe.format_value(unit_profit, {"fieldtype": "Currency"}),
            round(profit_rate, 1)
        )
    }


def calculate_jewelry_prices(doc, method=None):
    """
    Calculate jewelry prices for all items in a sales document
    Hook function for Sales Order, Sales Invoice, Quotation, POS Invoice

    Args:
        doc: The document (Sales Order, Sales Invoice, etc.)
        method: The event method (validate, etc.)
    """
    if not doc.get("items"):
        return

    transaction_date = doc.get("transaction_date") or doc.get("posting_date") or frappe.utils.today()

    updated_items = []

    for item in doc.items:
        item_code = item.get("item_code")
        if not item_code:
            continue

        # Check if item is jewelry
        is_jewelry = frappe.db.get_value("Item", item_code, "is_jewelry")
        if not is_jewelry:
            continue

        qty = float(item.get("qty") or 1)
        result = calculate_jewelry_price(item_code, qty, transaction_date)

        if result:
            # Update item rate
            item.rate = result["unit_price"]
            item.amount = result["total_price"]

            # Store breakdown in description if not already there
            breakdown_info = f"\n【价格计算】{result['breakdown']}"
            if breakdown_info not in (item.description or ""):
                item.description = (item.description or "") + breakdown_info

            updated_items.append({
                "item_code": item_code,
                "item_name": item.get("item_name"),
                "price": result["unit_price"],
                "breakdown": result["breakdown"]
            })

    if updated_items:
        frappe.msgprint(
            _("已自动计算 {0} 件珠宝商品价格").format(len(updated_items)),
            alert=True,
            indicator="green"
        )


@frappe.whitelist()
def get_jewelry_price_preview(item_code, qty=1):
    """
    API endpoint to preview jewelry price calculation
    Used by frontend JS

    Args:
        item_code: Item code
        qty: Quantity

    Returns:
        dict: Price calculation result
    """
    result = calculate_jewelry_price(item_code, float(qty or 1))
    return result
