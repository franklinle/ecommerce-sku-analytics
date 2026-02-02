-- Q2 2025 E-Commerce Analytics SQL Queries
-- These queries analyze SKU performance and daily metrics

-- ============================================================
-- 1. TOP SKUS BY NET PROFIT
-- Skills: ORDER BY, LIMIT, filtering
-- ============================================================
SELECT
    SKU,
    Category,
    Units_Sold,
    Revenue,
    Net_Profit,
    Margin_Pct,
    Performance_Tier
FROM sku_metrics
WHERE Net_Profit > 0
ORDER BY Net_Profit DESC
LIMIT 10;


-- ============================================================
-- 2. CATEGORY PERFORMANCE SUMMARY
-- Skills: GROUP BY, aggregation, RANK() window function
-- ============================================================
SELECT
    Category,
    COUNT(*) as SKU_Count,
    SUM(Units_Sold) as Total_Units,
    ROUND(SUM(Revenue), 2) as Total_Revenue,
    ROUND(SUM(Net_Profit), 2) as Total_Profit,
    ROUND(AVG(Margin_Pct), 2) as Avg_Margin,
    RANK() OVER (ORDER BY SUM(Net_Profit) DESC) as Profit_Rank
FROM sku_metrics
GROUP BY Category
ORDER BY Total_Profit DESC;


-- ============================================================
-- 3. DAILY RUNNING TOTAL & MOVING AVERAGE
-- Skills: SUM() OVER, window functions, rolling calculations
-- ============================================================
SELECT
    Date,
    Net_Profit,
    ROUND(SUM(Net_Profit) OVER (ORDER BY Date), 2) as Running_Total,
    ROUND(AVG(Net_Profit) OVER (
        ORDER BY Date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) as Profit_7day_MA
FROM daily_metrics
ORDER BY Date;


-- ============================================================
-- 4. WEEK-OVER-WEEK COMPARISON
-- Skills: CTEs, LAG() window function, percentage calculations
-- ============================================================
WITH weekly_stats AS (
    SELECT
        Week_Number,
        MIN(Date) as Week_Start,
        SUM(Net_Profit) as Weekly_Profit,
        SUM(Units_Sold) as Weekly_Units,
        SUM(Revenue) as Weekly_Revenue
    FROM daily_metrics
    GROUP BY Week_Number
)
SELECT
    Week_Number,
    Week_Start,
    ROUND(Weekly_Profit, 2) as Weekly_Profit,
    ROUND(LAG(Weekly_Profit) OVER (ORDER BY Week_Number), 2) as Prev_Week_Profit,
    ROUND(
        (Weekly_Profit - LAG(Weekly_Profit) OVER (ORDER BY Week_Number)) * 100.0
        / NULLIF(LAG(Weekly_Profit) OVER (ORDER BY Week_Number), 0),
        1
    ) as Profit_Change_Pct,
    Weekly_Units,
    ROUND(Weekly_Revenue, 2) as Weekly_Revenue
FROM weekly_stats
ORDER BY Week_Number;


-- ============================================================
-- 5. SKUS NEEDING ATTENTION
-- Skills: Complex WHERE conditions, CASE statements
-- ============================================================
SELECT
    SKU,
    Category,
    Units_Sold,
    Net_Profit,
    Margin_Pct,
    ROI_Pct,
    Refund_Rate_Pct,
    Health_Score,
    Performance_Tier,
    CASE
        WHEN Net_Profit < 0 THEN 'Losing Money'
        WHEN Refund_Rate_Pct > 15 THEN 'High Refunds'
        WHEN Margin_Pct < 5 THEN 'Low Margin'
        WHEN ROI_Pct < 10 THEN 'Low ROI'
        ELSE 'Other Issues'
    END as Issue_Type
FROM sku_metrics
WHERE Performance_Tier IN ('Weak', 'Liquidate')
   OR Net_Profit < 0
   OR Refund_Rate_Pct > 20
ORDER BY Net_Profit ASC;


-- ============================================================
-- 6. REFUND RATE OUTLIERS
-- Skills: Subqueries, statistical thresholds
-- ============================================================
SELECT
    SKU,
    Category,
    Units_Sold,
    Refunds,
    Refund_Rate_Pct,
    Net_Profit,
    Performance_Tier
FROM sku_metrics
WHERE Refund_Rate_Pct > (
    SELECT AVG(Refund_Rate_Pct) + STDEV(Refund_Rate_Pct)
    FROM sku_metrics
    WHERE Refund_Rate_Pct > 0
)
ORDER BY Refund_Rate_Pct DESC;


-- ============================================================
-- 7. DAY OF WEEK PERFORMANCE PATTERN
-- Skills: Categorical grouping, custom sorting, aggregation
-- ============================================================
SELECT
    Day_of_Week,
    COUNT(*) as Days_Count,
    ROUND(AVG(Net_Profit), 2) as Avg_Profit,
    ROUND(AVG(Units_Sold), 1) as Avg_Units,
    ROUND(AVG(Revenue), 2) as Avg_Revenue,
    ROUND(AVG(Conversion_Rate_Pct), 2) as Avg_Conversion,
    ROUND(SUM(Net_Profit), 2) as Total_Profit
FROM daily_metrics
GROUP BY Day_of_Week
ORDER BY
    CASE Day_of_Week
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;


-- ============================================================
-- 8. TIER DISTRIBUTION WITH PERCENTAGES
-- Skills: Window functions for percentage calculations
-- ============================================================
SELECT
    Performance_Tier,
    COUNT(*) as SKU_Count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as Pct_of_Portfolio,
    ROUND(SUM(Net_Profit), 2) as Total_Profit,
    ROUND(SUM(Net_Profit) * 100.0 / SUM(SUM(Net_Profit)) OVER (), 1) as Pct_of_Profit,
    ROUND(AVG(Health_Score), 0) as Avg_Health_Score
FROM sku_metrics
GROUP BY Performance_Tier
ORDER BY Avg_Health_Score DESC;
