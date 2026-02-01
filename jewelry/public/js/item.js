frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Add button to preview price calculation for jewelry items
        if (frm.doc.is_jewelry && frm.doc.metal_type && frm.doc.net_weight) {
            frm.add_custom_button(__('预览价格和利润'), function() {
                frappe.call({
                    method: 'jewelry.utils.pricing.get_jewelry_price_preview',
                    args: {
                        item_code: frm.doc.item_code,
                        qty: 1
                    },
                    callback: function(r) {
                        if (r.message) {
                            let result = r.message;
                            let profit_color = result.unit_profit >= 0 ? 'green' : 'red';
                            frappe.msgprint({
                                title: __('价格和利润预览'),
                                indicator: 'green',
                                message: `
                                    <h4>售价计算</h4>
                                    <table class="table table-bordered">
                                        <tr>
                                            <th>金属类型</th>
                                            <td>${frm.doc.metal_type}</td>
                                        </tr>
                                        <tr>
                                            <th>今日金价</th>
                                            <td>${format_currency(result.gold_price_per_gram)}/克</td>
                                        </tr>
                                        <tr>
                                            <th>净重</th>
                                            <td>${result.net_weight} 克</td>
                                        </tr>
                                        <tr>
                                            <th>金价小计</th>
                                            <td>${format_currency(result.base_price)}</td>
                                        </tr>
                                        <tr>
                                            <th>工费</th>
                                            <td>${format_currency(result.making_charge)}</td>
                                        </tr>
                                        <tr>
                                            <th><strong>售价</strong></th>
                                            <td><strong>${format_currency(result.unit_price)}</strong></td>
                                        </tr>
                                    </table>
                                    <h4>成本和利润</h4>
                                    <table class="table table-bordered">
                                        <tr>
                                            <th>金料成本</th>
                                            <td>${format_currency(result.gold_cost)} (${format_currency(result.gold_cost_price)}/克 × ${result.net_weight}克)</td>
                                        </tr>
                                        <tr>
                                            <th>工费成本</th>
                                            <td>${format_currency(result.making_cost)}</td>
                                        </tr>
                                        <tr>
                                            <th>其他成本</th>
                                            <td>${format_currency(result.other_cost)}</td>
                                        </tr>
                                        <tr>
                                            <th>总成本</th>
                                            <td>${format_currency(result.total_cost)}</td>
                                        </tr>
                                        <tr style="color: ${profit_color}">
                                            <th><strong>利润</strong></th>
                                            <td><strong>${format_currency(result.unit_profit)} (${result.profit_rate.toFixed(1)}%)</strong></td>
                                        </tr>
                                    </table>
                                    <p class="text-muted">${result.profit_breakdown}</p>
                                `
                            });
                        } else {
                            frappe.msgprint(__('无法计算价格，请检查是否已录入今日金价'));
                        }
                    }
                });
            }, __('珠宝'));
        }

        // Calculate total cost when cost fields change
        if (frm.doc.is_jewelry) {
            frm.trigger('calculate_total_cost');
        }
    },

    is_jewelry: function(frm) {
        if (!frm.doc.is_jewelry) {
            frm.set_value('metal_type', '');
            frm.set_value('net_weight', 0);
            frm.set_value('making_charge_type', '按件');
            frm.set_value('making_charge', 0);
            frm.set_value('gold_cost_price', 0);
            frm.set_value('making_cost', 0);
            frm.set_value('other_cost', 0);
            frm.set_value('total_cost', 0);
        }
    },

    metal_type: function(frm) {
        if (frm.doc.is_jewelry && frm.doc.metal_type) {
            frappe.call({
                method: 'jewelry.utils.pricing.get_jewelry_price_preview',
                args: {
                    item_code: frm.doc.item_code || frm.doc.name,
                    qty: 1
                },
                callback: function(r) {
                    if (r.message && r.message.gold_price_per_gram) {
                        frappe.show_alert({
                            message: __('今日{0}价格: {1}/克', [
                                frm.doc.metal_type,
                                format_currency(r.message.gold_price_per_gram)
                            ]),
                            indicator: 'blue'
                        }, 5);
                    }
                }
            });
        }
    },

    gold_cost_price: function(frm) {
        frm.trigger('calculate_total_cost');
    },

    making_cost: function(frm) {
        frm.trigger('calculate_total_cost');
    },

    other_cost: function(frm) {
        frm.trigger('calculate_total_cost');
    },

    net_weight: function(frm) {
        frm.trigger('calculate_total_cost');
    },

    calculate_total_cost: function(frm) {
        if (frm.doc.is_jewelry) {
            let gold_cost = (frm.doc.gold_cost_price || 0) * (frm.doc.net_weight || 0);
            let total = gold_cost + (frm.doc.making_cost || 0) + (frm.doc.other_cost || 0);
            frm.set_value('total_cost', total);
        }
    }
});
