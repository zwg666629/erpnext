frappe.ui.form.on('Trade In Transaction', {
    refresh: function(frm) {
        if (frm.doc.old_gold_purity && !frm.doc.recycling_price) {
            frm.trigger('old_gold_purity');
        }
    },

    old_gold_purity: function(frm) {
        if (frm.doc.old_gold_purity) {
            frappe.call({
                method: 'jewelry.jewelry.doctype.trade_in_transaction.trade_in_transaction.get_recycling_price',
                args: {
                    metal_type: frm.doc.old_gold_purity,
                    date: frm.doc.transaction_date
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('recycling_price', r.message);
                        frappe.show_alert({
                            message: __('已获取{0}回收价: {1}/克', [frm.doc.old_gold_purity, format_currency(r.message)]),
                            indicator: 'blue'
                        }, 5);
                    }
                }
            });
        }
    },

    old_gold_weight: function(frm) {
        frm.trigger('calculate_value');
    },

    recycling_price: function(frm) {
        frm.trigger('calculate_value');
    },

    purity_discount: function(frm) {
        frm.trigger('calculate_value');
    },

    new_item_total: function(frm) {
        frm.trigger('calculate_value');
    },

    calculate_value: function(frm) {
        let weight = frm.doc.old_gold_weight || 0;
        let price = frm.doc.recycling_price || 0;
        let discount = (frm.doc.purity_discount || 100) / 100;

        let old_value = weight * price * discount;
        frm.set_value('old_gold_value', old_value);

        let new_total = frm.doc.new_item_total || 0;
        let deduction = Math.min(old_value, new_total);
        frm.set_value('trade_in_deduction', deduction);
        frm.set_value('amount_payable', new_total - deduction);
    }
});
