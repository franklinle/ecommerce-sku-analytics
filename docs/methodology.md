# Methodology Documentation

## Overview

This document details the data processing methodology, analytical approach, and business logic used in the Q2 2025 SKU Profitability & Velocity Analysis project.

## Data Sources

### Primary Data Source: Sellerboard
- **Platform**: Amazon Seller analytics tool
- **Export Format**: CSV with European number formatting
- **Time Period**: Q2 2025 (March 31 - June 30, 2025)
- **Scope**: 90 active SKUs across 10 product categories

### Data Exports Used
1. **SKU-Level Report**: Product performance metrics
2. **Daily Metrics Report**: Time-series transaction data

## Data Cleaning Process

### 1. European Number Format Conversion

Sellerboard exports use European formatting which requires conversion:

| Original | Converted |
|----------|-----------|
| `5 191,16` | `5191.16` |
| `1 234,56` | `1234.56` |

**Logic**: Remove space (thousands separator) and replace comma with period (decimal separator).

### 2. Product Name Parsing

Raw product names contained embedded metadata that needed to be stripped:
- COG (Cost of Goods) values
- Price information
- Internal reference codes

### 3. Category Assignment

Implemented keyword-based classification into 10 categories:

| Category | Keywords |
|----------|----------|
| Electronics & Home | electronic, cable, charger, adapter, battery, home, kitchen |
| Fragrances | perfume, cologne, fragrance, scent |
| Beauty & Skincare | beauty, skincare, cream, lotion, makeup |
| Consumables & Health | vitamin, supplement, health, protein, snack |
| Collectibles & Toys | toy, collectible, figure, game, puzzle |
| Apparel & Footwear | shirt, pants, shoes, clothing, jacket |
| Drinkware | mug, cup, bottle, tumbler |
| Sports | sport, fitness, exercise, gym |
| Media & Entertainment | book, dvd, cd, media |
| Other | Default for unmatched products |

### 4. Data Anonymization

Replaced actual SKU identifiers with anonymous IDs (SKU-0001 through SKU-0090) for portfolio sharing while preserving analytical value.

## Calculated Metrics

### SKU-Level Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| Net Profit | Revenue - COGS - Amazon Fees | Bottom-line profitability |
| Margin % | (Net Profit / Revenue) × 100 | Profitability efficiency |
| ROI % | (Net Profit / COGS) × 100 | Return on investment |
| Refund Rate % | (Refunds / Units Sold) × 100 | Product quality indicator |
| Profit Per Unit | Net Profit / Units Sold | Unit economics |

### Time-Series Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| 7-Day Moving Average | Rolling mean of last 7 days | Trend smoothing |
| Conversion Rate % | (Orders / Sessions) × 100 | Traffic efficiency |
| Week Number | ISO week number | Weekly aggregation |

## Health Score Algorithm

The health score is a composite metric (0-100 scale) evaluating four performance dimensions:

### Scoring Components

#### 1. Profit Contribution (max +20 / min -15 points)
| Condition | Score Adjustment |
|-----------|-----------------|
| Net Profit > $500 | +20 |
| Net Profit > $200 | +15 |
| Net Profit > $100 | +10 |
| Net Profit > $50 | +5 |
| Net Profit < $0 | -15 |

#### 2. Sales Velocity (max +15 / min -10 points)
| Condition | Score Adjustment |
|-----------|-----------------|
| Units > 50 | +15 |
| Units > 25 | +10 |
| Units > 10 | +5 |
| Units = 0 | -10 |

#### 3. ROI Performance (max +10 / min -10 points)
| Condition | Score Adjustment |
|-----------|-----------------|
| ROI > 50% | +10 |
| ROI > 25% | +5 |
| ROI < 0% | -10 |

#### 4. Margin Quality (max +5 / min -5 points)
| Condition | Score Adjustment |
|-----------|-----------------|
| Margin > 20% | +5 |
| Margin < 5% | -5 |

### Performance Tier Assignment

| Health Score | Tier | Recommended Action |
|--------------|------|-------------------|
| 80-100 | Star | Scale up - increase inventory |
| 60-79 | Strong | Maintain - steady restocking |
| 45-59 | Average | Monitor - watch for improvement |
| 0-44 | Weak | Review/Liquidate - reduce exposure |

## SQL Analysis Approach

### Query Categories

1. **Descriptive Analytics**: Top performers, category summaries
2. **Time-Series Analysis**: Running totals, moving averages, WoW comparisons
3. **Diagnostic Analytics**: Identifying problem SKUs, outlier detection
4. **Pattern Recognition**: Day-of-week effects, seasonal patterns

### Key SQL Techniques Demonstrated
- Window functions (`RANK()`, `LAG()`, `SUM() OVER`)
- Common Table Expressions (CTEs)
- Conditional aggregation (`CASE` statements)
- Subqueries for statistical thresholds

## Visualization Design Principles

### Dashboard Layout
- **Top**: KPI cards for executive summary
- **Middle**: Category and trend visualizations
- **Bottom**: Detailed drill-down tables

### Color Scheme
- Green: Positive performance / Star tier
- Blue: Neutral / Strong tier
- Yellow: Caution / Average tier
- Red: Attention needed / Weak tier

### Interactivity
- Click-to-filter on categories
- Hover tooltips with detailed metrics
- Sortable data tables

## Limitations & Assumptions

### Data Limitations
1. Single quarter of data limits trend analysis
2. Session data may have tracking gaps
3. External factors (seasonality, promotions) not captured

### Assumptions
1. COGS values are accurate and current
2. Amazon fee structures remained constant during Q2
3. Refunds are processed within the same quarter

## Future Enhancements

1. **Inventory Optimization**: Calculate reorder points and stockout costs
2. **Predictive Modeling**: Forecast daily profit using time-series models
3. **Automated Pipeline**: Schedule regular data refreshes
4. **Multi-Quarter Analysis**: Compare performance across periods
