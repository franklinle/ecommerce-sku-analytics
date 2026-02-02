"""
Q2 2025 E-Commerce SKU Data Transformation Script

This script processes raw Sellerboard CSV exports and prepares them for
Tableau visualization. It handles data cleaning, category assignment,
and health score calculation.

Author: Franklin Le
"""

import pandas as pd
import numpy as np
from pathlib import Path


def clean_european_number(value):
    """
    Convert European number format to standard float.
    European: 5 191,16 -> 5191.16 (space=thousands, comma=decimal)
    """
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    # Remove spaces (thousands separator) and replace comma with period
    cleaned = str(value).replace(' ', '').replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def assign_category(product_name):
    """
    Assign product category based on keywords in product name.
    Returns one of 10 predefined categories.
    """
    name_lower = str(product_name).lower()

    category_keywords = {
        'Electronics & Home': ['electronic', 'cable', 'charger', 'adapter', 'battery',
                               'home', 'kitchen', 'appliance', 'tool'],
        'Fragrances': ['perfume', 'cologne', 'fragrance', 'scent', 'eau de'],
        'Beauty & Skincare': ['beauty', 'skincare', 'cream', 'lotion', 'makeup',
                              'cosmetic', 'serum', 'face'],
        'Consumables & Health': ['vitamin', 'supplement', 'health', 'protein',
                                  'snack', 'food', 'drink', 'consumable'],
        'Collectibles & Toys': ['toy', 'collectible', 'figure', 'game', 'puzzle', 'lego'],
        'Apparel & Footwear': ['shirt', 'pants', 'shoes', 'clothing', 'apparel',
                               'jacket', 'dress', 'footwear'],
        'Drinkware': ['mug', 'cup', 'bottle', 'tumbler', 'glass', 'drinkware'],
        'Sports': ['sport', 'fitness', 'exercise', 'gym', 'outdoor', 'athletic'],
        'Media & Entertainment': ['book', 'dvd', 'cd', 'media', 'movie', 'music'],
    }

    for category, keywords in category_keywords.items():
        if any(kw in name_lower for kw in keywords):
            return category

    return 'Other'


def calculate_health_score(row):
    """
    Calculate composite health score (0-100) based on four performance dimensions:
    - Profit contribution
    - Sales velocity (units sold)
    - ROI percentage
    - Margin percentage
    """
    score = 50  # Base score

    # Profit contribution (max +20 / min -15)
    net_profit = row.get('Net_Profit', 0)
    if net_profit > 500:
        score += 20
    elif net_profit > 200:
        score += 15
    elif net_profit > 100:
        score += 10
    elif net_profit > 50:
        score += 5
    elif net_profit < 0:
        score -= 15

    # Velocity/Units sold (max +15 / min -10)
    units = row.get('Units_Sold', 0)
    if units > 50:
        score += 15
    elif units > 25:
        score += 10
    elif units > 10:
        score += 5
    elif units == 0:
        score -= 10

    # ROI (max +10 / min -10)
    roi = row.get('ROI_Pct', 0)
    if roi > 50:
        score += 10
    elif roi > 25:
        score += 5
    elif roi < 0:
        score -= 10

    # Margin (max +5 / min -5)
    margin = row.get('Margin_Pct', 0)
    if margin > 20:
        score += 5
    elif margin < 5:
        score -= 5

    return max(0, min(100, score))


def assign_performance_tier(health_score):
    """
    Assign performance tier based on health score.
    """
    if health_score >= 80:
        return 'Star'
    elif health_score >= 60:
        return 'Strong'
    elif health_score >= 45:
        return 'Average'
    else:
        return 'Weak'


def process_sku_data(input_path, output_path):
    """
    Process raw SKU-level data from Sellerboard export.
    """
    print(f"Processing SKU data from {input_path}...")

    # Read raw data
    df = pd.read_csv(input_path)

    # Clean numeric columns (handle European formatting if present)
    numeric_cols = ['Revenue', 'COGS', 'Amazon_Fees', 'Net_Profit']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_european_number)

    # Calculate derived metrics
    df['Margin_Pct'] = np.where(
        df['Revenue'] > 0,
        (df['Net_Profit'] / df['Revenue']) * 100,
        0
    )

    df['ROI_Pct'] = np.where(
        df['COGS'].abs() > 0,
        (df['Net_Profit'] / df['COGS'].abs()) * 100,
        0
    )

    df['Refund_Rate_Pct'] = np.where(
        df['Units_Sold'] > 0,
        (df['Refunds'] / df['Units_Sold']) * 100,
        0
    )

    df['Avg_Sale_Price'] = np.where(
        df['Units_Sold'] > 0,
        df['Revenue'] / df['Units_Sold'],
        0
    )

    df['Profit_Per_Unit'] = np.where(
        df['Units_Sold'] > 0,
        df['Net_Profit'] / df['Units_Sold'],
        0
    )

    # Calculate health score and tier
    df['Health_Score'] = df.apply(calculate_health_score, axis=1)
    df['Performance_Tier'] = df['Health_Score'].apply(assign_performance_tier)

    # Anonymize SKUs
    df['SKU'] = [f'SKU-{str(i+1).zfill(4)}' for i in range(len(df))]

    # Save processed data
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} SKUs to {output_path}")

    return df


def process_daily_data(input_path, output_path):
    """
    Process raw daily metrics from Sellerboard export.
    """
    print(f"Processing daily data from {input_path}...")

    # Read raw data
    df = pd.read_csv(input_path)

    # Ensure date is properly formatted
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    # Calculate 7-day moving averages
    df['Profit_7day_MA'] = df['Net_Profit'].rolling(window=7, min_periods=1).mean()
    df['Units_7day_MA'] = df['Units_Sold'].rolling(window=7, min_periods=1).mean()
    df['Revenue_7day_MA'] = df['Revenue'].rolling(window=7, min_periods=1).mean()

    # Add time-based columns
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Week_Number'] = df['Date'].dt.isocalendar().week

    # Calculate conversion rate
    df['Conversion_Rate_Pct'] = np.where(
        df['Sessions'] > 0,
        (df['Orders'] / df['Sessions']) * 100,
        0
    )

    # Calculate daily margin
    df['Margin_Pct'] = np.where(
        df['Revenue'] > 0,
        (df['Net_Profit'] / df['Revenue']) * 100,
        0
    )

    # Save processed data
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} daily records to {output_path}")

    return df


def generate_summary_stats(sku_df, daily_df):
    """
    Generate and print summary statistics for the processed data.
    """
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    # Key metrics
    total_profit = sku_df['Net_Profit'].sum()
    total_units = sku_df['Units_Sold'].sum()
    total_revenue = sku_df['Revenue'].sum()
    avg_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    print(f"\nTotal Net Profit: ${total_profit:,.2f}")
    print(f"Total Units Sold: {int(total_units):,}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Average Margin: {avg_margin:.1f}%")
    print(f"Active SKUs: {len(sku_df)}")
    print(f"Avg Daily Profit: ${total_profit / len(daily_df):.2f}")

    # Category breakdown
    print("\nCategory Performance:")
    category_stats = sku_df.groupby('Category').agg({
        'Net_Profit': 'sum',
        'SKU': 'count'
    }).sort_values('Net_Profit', ascending=False)

    for cat, row in category_stats.iterrows():
        pct = row['Net_Profit'] / total_profit * 100
        print(f"  {cat}: ${row['Net_Profit']:,.2f} ({pct:.1f}%) - {int(row['SKU'])} SKUs")

    # Tier distribution
    print("\nPerformance Tier Distribution:")
    tier_stats = sku_df['Performance_Tier'].value_counts()
    for tier in ['Star', 'Strong', 'Average', 'Weak']:
        if tier in tier_stats:
            count = tier_stats[tier]
            pct = count / len(sku_df) * 100
            print(f"  {tier}: {count} ({pct:.0f}%)")


def main():
    """
    Main execution function.
    """
    # Define paths
    base_path = Path(__file__).parent.parent
    data_path = base_path / 'data'

    # Process SKU data (assuming raw file exists)
    sku_output = data_path / 'tableau_sku_data.csv'
    daily_output = data_path / 'tableau_daily_data.csv'

    # Check if processed files already exist
    if sku_output.exists() and daily_output.exists():
        print("Processed data files already exist.")
        print("Loading existing files for summary...")
        sku_df = pd.read_csv(sku_output)
        daily_df = pd.read_csv(daily_output)
        generate_summary_stats(sku_df, daily_df)
    else:
        print("Raw data files not found. Please place Sellerboard exports in data/ directory.")
        print("Expected files: raw_sku_data.csv, raw_daily_data.csv")


if __name__ == '__main__':
    main()
