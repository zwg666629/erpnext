import frappe
from frappe.model.document import Document


class DailyGoldPrice(Document):
    def validate(self):
        self.validate_prices()

    def validate_prices(self):
        """Ensure at least one price is entered and all prices are non-negative"""
        price_fields = [
            "gold_999_price",
            "gold_990_price",
            "gold_750_price",
            "gold_916_price",
            "platinum_price",
            "silver_price"
        ]

        has_price = False
        for field in price_fields:
            value = self.get(field)
            if value:
                if value < 0:
                    frappe.throw(f"价格不能为负数: {self.meta.get_label(field)}")
                has_price = True

        if not has_price:
            frappe.throw("请至少输入一种金属的价格")


def get_gold_price_for_date(date=None, metal_type=None):
    """
    Get gold price for a specific date and metal type

    Args:
        date: The date to get price for (defaults to today)
        metal_type: Metal type (足金999/足金990/18K金/22K金/铂金/银)

    Returns:
        float: Price per gram, or 0 if not found
    """
    if not date:
        date = frappe.utils.today()

    metal_field_map = {
        "足金999": "gold_999_price",
        "足金990": "gold_990_price",
        "18K金": "gold_750_price",
        "22K金": "gold_916_price",
        "铂金": "platinum_price",
        "银": "silver_price"
    }

    field = metal_field_map.get(metal_type)
    if not field:
        return 0

    price_doc = frappe.db.get_value(
        "Daily Gold Price",
        {"date": date},
        field
    )

    if price_doc:
        return float(price_doc)

    # If no price for today, get the most recent price
    recent_price = frappe.db.sql("""
        SELECT {field}
        FROM `tabDaily Gold Price`
        WHERE date <= %s AND {field} > 0
        ORDER BY date DESC
        LIMIT 1
    """.format(field=field), (date,), as_dict=True)

    if recent_price and recent_price[0].get(field):
        return float(recent_price[0].get(field))

    return 0
