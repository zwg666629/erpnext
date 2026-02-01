import frappe
from frappe import _
from frappe.utils import flt


class TradeInTransaction(frappe.model.document.Document):
    def validate(self):
        self.calculate_old_gold_value()
        self.calculate_payable()

    def calculate_old_gold_value(self):
        """计算旧金价值 = 克重 × 回收单价 × 成色折扣"""
        weight = flt(self.old_gold_weight)
        price = flt(self.recycling_price)
        discount = flt(self.purity_discount) / 100 if self.purity_discount else 1

        self.old_gold_value = weight * price * discount

    def calculate_payable(self):
        """计算应付金额 = 新品总价 - 旧金抵扣"""
        old_value = flt(self.old_gold_value)
        new_total = flt(self.new_item_total)

        # 抵扣金额不能超过新品总价
        self.trade_in_deduction = min(old_value, new_total)
        self.amount_payable = new_total - self.trade_in_deduction


@frappe.whitelist()
def get_recycling_price(metal_type, date=None):
    """获取当日回收金价（通常为销售价的一定比例）"""
    from jewelry.jewelry.doctype.daily_gold_price.daily_gold_price import get_gold_price_for_date

    selling_price = get_gold_price_for_date(date, metal_type)
    if selling_price:
        # 回收价通常为销售价的 95-98%
        recycling_rate = 0.95
        return flt(selling_price) * recycling_rate
    return 0


@frappe.whitelist()
def create_trade_in_from_pos(pos_invoice, old_gold_purity, old_gold_weight, recycling_price, purity_discount=100):
    """从POS创建以旧换新单"""
    pos = frappe.get_doc("POS Invoice", pos_invoice)

    trade_in = frappe.new_doc("Trade In Transaction")
    trade_in.transaction_date = pos.posting_date
    trade_in.customer = pos.customer
    trade_in.company = pos.company
    trade_in.pos_invoice = pos_invoice
    trade_in.new_item_total = pos.grand_total
    trade_in.old_gold_purity = old_gold_purity
    trade_in.old_gold_weight = flt(old_gold_weight)
    trade_in.recycling_price = flt(recycling_price)
    trade_in.purity_discount = flt(purity_discount)

    trade_in.insert()
    trade_in.status = "已完成"
    trade_in.save()

    return trade_in.name
