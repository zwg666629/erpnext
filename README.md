# Jewelry Dynamic Pricing Module

珠宝行业动态定价模块 for ERPNext

## Features

- 每日金价录入和管理
- 销售时自动计算价格：金价 × 克重 + 工费
- 支持多种金属类型（足金999/990、18K、22K、铂金、银）
- 支持按件/按克工费计算

## Installation

```bash
bench get-app jewelry
bench --site your-site install-app jewelry
```

## Usage

1. 录入每日金价：珠宝 > 每日金价
2. 创建珠宝商品：勾选"是否珠宝商品"，设置金属类型、克重、工费
3. 创建销售订单/发票，价格自动计算
