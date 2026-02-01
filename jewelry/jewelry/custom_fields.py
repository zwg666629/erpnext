import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def get_custom_fields():
    """Define custom fields for Item doctype"""
    return {
        "Item": [
            {
                "fieldname": "jewelry_section",
                "fieldtype": "Section Break",
                "label": "珠宝信息",
                "insert_after": "description",
                "collapsible": 1,
                "depends_on": "eval:doc.is_jewelry"
            },
            {
                "fieldname": "is_jewelry",
                "fieldtype": "Check",
                "label": "是否珠宝商品",
                "insert_after": "is_stock_item",
                "default": "0",
                "description": "勾选后可设置金属类型、克重和工费，销售时自动计算价格"
            },
            {
                "fieldname": "metal_type",
                "fieldtype": "Select",
                "label": "金属类型",
                "insert_after": "jewelry_section",
                "options": "\n足金999\n足金990\n18K金\n22K金\n铂金\n银",
                "depends_on": "eval:doc.is_jewelry",
                "mandatory_depends_on": "eval:doc.is_jewelry"
            },
            {
                "fieldname": "net_weight",
                "fieldtype": "Float",
                "label": "净重（克）",
                "insert_after": "metal_type",
                "precision": "3",
                "depends_on": "eval:doc.is_jewelry",
                "mandatory_depends_on": "eval:doc.is_jewelry",
                "description": "珠宝商品的金属净重（克）"
            },
            {
                "fieldname": "making_charge_type",
                "fieldtype": "Select",
                "label": "工费类型",
                "insert_after": "net_weight",
                "options": "按件\n按克",
                "default": "按件",
                "depends_on": "eval:doc.is_jewelry"
            },
            {
                "fieldname": "making_charge",
                "fieldtype": "Currency",
                "label": "工费金额",
                "insert_after": "making_charge_type",
                "precision": "2",
                "depends_on": "eval:doc.is_jewelry",
                "description": "按件：每件工费金额；按克：每克工费金额"
            },
            {
                "fieldname": "cost_column_break",
                "fieldtype": "Column Break",
                "insert_after": "making_charge"
            },
            {
                "fieldname": "gold_cost_price",
                "fieldtype": "Currency",
                "label": "金料成本价（元/克）",
                "insert_after": "cost_column_break",
                "precision": "2",
                "depends_on": "eval:doc.is_jewelry",
                "description": "进货时的金价成本"
            },
            {
                "fieldname": "making_cost",
                "fieldtype": "Currency",
                "label": "工费成本",
                "insert_after": "gold_cost_price",
                "precision": "2",
                "depends_on": "eval:doc.is_jewelry",
                "description": "实际工费成本"
            },
            {
                "fieldname": "other_cost",
                "fieldtype": "Currency",
                "label": "其他成本",
                "insert_after": "making_cost",
                "precision": "2",
                "depends_on": "eval:doc.is_jewelry",
                "description": "镶嵌、宝石等其他成本"
            },
            {
                "fieldname": "total_cost",
                "fieldtype": "Currency",
                "label": "总成本",
                "insert_after": "other_cost",
                "precision": "2",
                "depends_on": "eval:doc.is_jewelry",
                "read_only": 1,
                "description": "金料成本 + 工费成本 + 其他成本"
            }
        ]
    }


def create_custom_fields_for_jewelry():
    """Create all custom fields"""
    custom_fields = get_custom_fields()
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
